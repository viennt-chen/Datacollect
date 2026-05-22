"""
事件数据关联服务
功能：根据event_data的时间范围匹配SV/PV/报警数据
"""
import gzip
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from app.models.event_data import EventData
from app.models.sv_compressed_param import SVCompressedParam
from app.models.pv_compressed_param import PVCompressedParam
from app.models.alarm_record import AlarmRecord
from app.models.event_relations import (
    EventSVRelation,
    EventPVRelation,
    EventAlarmRelation,
    EventDataRelationSummary
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventDataRelationService:
    """事件数据关联服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def decompress_payload(self, compressed_data: bytes) -> Dict[str, Any]:
        """解压缩payload数据"""
        try:
            decompressed = gzip.decompress(compressed_data).decode('utf-8')
            return json.loads(decompressed)
        except Exception as e:
            logger.error(f"解压缩失败：{e}")
            return {}
    
    def match_and_save_relations(self, event_id: int) -> Dict[str, int]:
        """
        为指定事件匹配并保存SV/PV/报警关联
        
        Args:
            event_id: 事件ID
            
        Returns:
            匹配结果：{"sv": count, "pv": count, "alarm": count}
        """
        event = self.db.query(EventData).filter(EventData.id == event_id).first()
        if not event:
            logger.warning(f"事件不存在：event_id={event_id}")
            return {"sv": 0, "pv": 0, "alarm": 0}
        
        if not event.start_time or not event.end_time:
            logger.warning(f"事件时间不完整：event_id={event_id}")
            return {"sv": 0, "pv": 0, "alarm": 0}
        
        logger.info(f"开始匹配事件关联：event_id={event_id}, machine_id={event.machine_id}")
        
        sv_count = self._match_sv_data(event)
        pv_count = self._match_pv_data(event)
        alarm_count = self._match_alarm_data(event)
        
        self._update_relation_summary(event, sv_count, pv_count, alarm_count)
        
        logger.info(f"事件关联匹配完成：event_id={event_id}, SV={sv_count}, PV={pv_count}, Alarm={alarm_count}")
        
        return {"sv": sv_count, "pv": pv_count, "alarm": alarm_count}
    
    def _match_sv_data(self, event: EventData) -> int:
        """匹配SV数据"""
        start_dt = datetime.fromtimestamp(event.start_time / 1000)
        end_dt = datetime.fromtimestamp(event.end_time / 1000)
        
        sv_records = self.db.query(SVCompressedParam).filter(
            and_(
                SVCompressedParam.timestamp >= start_dt,
                SVCompressedParam.timestamp <= end_dt,
                SVCompressedParam.topic.contains(event.machine_id)
            )
        ).order_by(SVCompressedParam.timestamp).all()
        
        count = 0
        for sv_record in sv_records:
            existing = self.db.query(EventSVRelation).filter(
                and_(
                    EventSVRelation.event_id == event.id,
                    EventSVRelation.sv_record_id == sv_record.id
                )
            ).first()
            
            if existing:
                continue
            
            sv_data = self.decompress_payload(sv_record.compressed_payload)
            
            relation = EventSVRelation(
                event_id=event.id,
                machine_id=event.machine_id,
                sv_topic=sv_record.topic,
                sv_record_id=sv_record.id,
                sv_data_snapshot=sv_data,
                sv_timestamp=sv_record.timestamp,
                time_offset_ms=int((sv_record.timestamp - start_dt).total_seconds() * 1000)
            )
            
            self.db.add(relation)
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def _match_pv_data(self, event: EventData) -> int:
        """匹配PV数据"""
        start_dt = datetime.fromtimestamp(event.start_time / 1000)
        end_dt = datetime.fromtimestamp(event.end_time / 1000)
        
        pv_records = self.db.query(PVCompressedParam).filter(
            and_(
                PVCompressedParam.timestamp >= start_dt,
                PVCompressedParam.timestamp <= end_dt,
                PVCompressedParam.topic.contains(event.machine_id)
            )
        ).order_by(PVCompressedParam.timestamp).all()

        count = 0
        for pv_record in pv_records:
            existing = self.db.query(EventPVRelation).filter(
                and_(
                    EventPVRelation.event_id == event.id,
                    EventPVRelation.pv_record_id == pv_record.id
                )
            ).first()

            if existing:
                continue

            pv_data = self.decompress_payload(pv_record.compressed_payload)

            relation = EventPVRelation(
                event_id=event.id,
                machine_id=event.machine_id,
                pv_topic=pv_record.topic,
                pv_record_id=pv_record.id,
                pv_data_snapshot=pv_data,
                pv_timestamp=pv_record.timestamp,
                time_offset_ms=int((pv_record.timestamp - start_dt).total_seconds() * 1000)
            )
            
            self.db.add(relation)
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def _match_alarm_data(self, event: EventData) -> int:
        """匹配报警数据"""
        start_dt = datetime.fromtimestamp(event.start_time / 1000)
        end_dt = datetime.fromtimestamp(event.end_time / 1000)
        
        alarms = self.db.query(AlarmRecord).filter(
            and_(
                AlarmRecord.alarm_time >= start_dt,
                AlarmRecord.alarm_time <= end_dt,
                or_(
                    AlarmRecord.device_code == event.machine_id,
                    AlarmRecord.device_code.is_(None)
                )
            )
        ).order_by(AlarmRecord.alarm_time).all()
        
        count = 0
        for alarm in alarms:
            existing = self.db.query(EventAlarmRelation).filter(
                and_(
                    EventAlarmRelation.event_id == event.id,
                    EventAlarmRelation.alarm_record_id == alarm.id
                )
            ).first()
            
            if existing:
                continue
            
            time_offset = int((alarm.alarm_time - start_dt).total_seconds() * 1000)
            
            relation = EventAlarmRelation(
                event_id=event.id,
                machine_id=event.machine_id,
                alarm_record_id=alarm.id,
                alarm_code=alarm.alarm_code,
                alarm_level=alarm.alarm_level,
                alarm_type=alarm.alarm_type,
                alarm_title=alarm.title,
                alarm_value=str(alarm.alarm_value) if alarm.alarm_value else None,
                alarm_time=alarm.alarm_time,
                time_offset_from_start_ms=time_offset
            )
            
            self.db.add(relation)
            count += 1
        
        if count > 0:
            self.db.commit()
        
        return count

    def _update_relation_summary(
        self, 
        event: EventData, 
        sv_count: int, 
        pv_count: int, 
        alarm_count: int
    ):
        """更新关联汇总信息"""
        summary = self.db.query(EventDataRelationSummary).filter(
            EventDataRelationSummary.event_id == event.id
        ).first()
        
        if not summary:
            summary = EventDataRelationSummary(
                event_id=event.id,
                machine_id=event.machine_id,
                event_start_time=event.start_time,
                event_end_time=event.end_time
            )
            self.db.add(summary)
        
        summary.sv_count = sv_count
        summary.pv_count = pv_count
        summary.alarm_count = alarm_count
        summary.sv_matched = 1 if sv_count > 0 else 0
        summary.pv_matched = 1 if pv_count > 0 else 0
        summary.alarm_matched = 1 if alarm_count > 0 else 0
        summary.last_match_time = datetime.now()
        
        self.db.commit()
    
    def batch_match_unmatched_events(self, limit: int = 100) -> Dict[str, int]:
        """
        批量匹配未关联的事件
        
        Args:
            limit: 每次处理的事件数量
            
        Returns:
            处理结果统计
        """
        unmatched_events = self.db.query(EventData).filter(
            ~EventData.id.in_(
                self.db.query(EventDataRelationSummary.event_id)
            )
        ).filter(
            EventData.start_time.isnot(None),
            EventData.end_time.isnot(None)
        ).order_by(EventData.start_time.desc()).limit(limit).all()
        
        total_sv = 0
        total_pv = 0
        total_alarm = 0
        
        for event in unmatched_events:
            try:
                result = self.match_and_save_relations(event.id)
                total_sv += result["sv"]
                total_pv += result["pv"]
                total_alarm += result["alarm"]
            except Exception as e:
                logger.error(f"匹配事件关联失败：event_id={event.id}, error={e}")
                self.db.rollback()
        
        logger.info(f"批量匹配完成：处理{len(unmatched_events)}个事件，SV={total_sv}, PV={total_pv}, Alarm={total_alarm}")
        
        return {
            "processed_events": len(unmatched_events),
            "sv_matched": total_sv,
            "pv_matched": total_pv,
            "alarm_matched": total_alarm
        }
    
    def get_event_relations(self, event_id: int) -> Dict[str, Any]:
        """
        获取事件的关联数据
        
        Args:
            event_id: 事件ID
            
        Returns:
            关联数据
        """
        summary = self.db.query(EventDataRelationSummary).filter(
            EventDataRelationSummary.event_id == event_id
        ).first()
        
        sv_relations = self.db.query(EventSVRelation).filter(
            EventSVRelation.event_id == event_id
        ).all()
        
        pv_relations = self.db.query(EventPVRelation).filter(
            EventPVRelation.event_id == event_id
        ).all()
        
        alarm_relations = self.db.query(EventAlarmRelation).filter(
            EventAlarmRelation.event_id == event_id
        ).all()
        
        return {
            "summary": {
                "event_id": summary.event_id if summary else None,
                "sv_count": summary.sv_count if summary else 0,
                "pv_count": summary.pv_count if summary else 0,
                "alarm_count": summary.alarm_count if summary else 0,
                "sv_matched": summary.sv_matched if summary else 0,
                "pv_matched": summary.pv_matched if summary else 0,
                "alarm_matched": summary.alarm_matched if summary else 0,
                "last_match_time": summary.last_match_time.isoformat() if summary and summary.last_match_time else None
            },
            "sv_data": [
                {
                    "id": rel.id,
                    "sv_topic": rel.sv_topic,
                    "sv_record_id": rel.sv_record_id,
                    "sv_data_snapshot": rel.sv_data_snapshot,
                    "sv_timestamp": rel.sv_timestamp.isoformat() if rel.sv_timestamp else None,
                    "time_offset_ms": rel.time_offset_ms
                }
                for rel in sv_relations
            ],
            "pv_data": [
                {
                    "id": rel.id,
                    "pv_topic": rel.pv_topic,
                    "pv_record_id": rel.pv_record_id,
                    "pv_data_snapshot": rel.pv_data_snapshot,
                    "pv_timestamp": rel.pv_timestamp.isoformat() if rel.pv_timestamp else None,
                    "time_offset_ms": rel.time_offset_ms,
                    "sv_point_id": rel.sv_point_id,
                    "sv_value_range": rel.sv_value_range
                }
                for rel in pv_relations
            ],
            "alarm_data": [
                {
                    "id": rel.id,
                    "alarm_record_id": rel.alarm_record_id,
                    "alarm_code": rel.alarm_code,
                    "alarm_level": rel.alarm_level,
                    "alarm_type": rel.alarm_type,
                    "alarm_title": rel.alarm_title,
                    "alarm_value": rel.alarm_value,
                    "alarm_time": rel.alarm_time.isoformat() if rel.alarm_time else None,
                    "time_offset_from_start_ms": rel.time_offset_from_start_ms
                }
                for rel in alarm_relations
            ]
        }
