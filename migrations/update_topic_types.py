"""
更新 MQTT Topic 配置表 - 将 compress 类型拆分为 pv_compress, sv_compress, alarm_compress
"""
import mysql.connector
import os
import sys

# 数据库配置
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '10.10.150.254'),
    'port': int(os.getenv('DB_PORT', '3306')),
    'user': os.getenv('DB_USER', 'datacollect'),
    'password': os.getenv('DB_PASSWORD', 'datacollect'),
    'database': os.getenv('DB_NAME', 'datacollect')
}


def update_topic_types():
    """更新 Topic 类型"""
    conn = None
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 查询所有 compress 类型的 Topic
        query_sql = """
        SELECT id, topic_name, description 
        FROM mqtt_topic_configs 
        WHERE topic_type = 'compress'
        """
        
        cursor.execute(query_sql)
        compress_topics = cursor.fetchall()
        
        if not compress_topics:
            print("✓ 没有需要更新的 compress 类型 Topic")
            return
        
        print(f"找到 {len(compress_topics)} 个 compress 类型 Topic，开始更新...\n")
        
        # 根据 topic_name 判断类型并更新
        for topic_id, topic_name, description in compress_topics:
            # 根据 topic_name 或 description 判断类型
            topic_upper = topic_name.upper()
            desc_upper = (description or '').upper()
            
            if 'PV' in topic_upper or 'PV' in desc_upper:
                new_type = 'pv_compress'
            elif 'SV' in topic_upper or 'SV' in desc_upper:
                new_type = 'sv_compress'
            elif 'ALARM' in topic_upper or 'ALARM' in desc_upper or '报警' in (description or ''):
                new_type = 'alarm_compress'
            else:
                # 默认根据 topic_name 最后一部分判断
                last_part = topic_name.split('/')[-1].upper()
                if last_part == 'PV':
                    new_type = 'pv_compress'
                elif last_part == 'SV':
                    new_type = 'sv_compress'
                elif last_part == 'ALARM':
                    new_type = 'alarm_compress'
                else:
                    print(f"- 无法判断类型，跳过：{topic_name}")
                    continue
            
            update_sql = """
            UPDATE mqtt_topic_configs 
            SET topic_type = %s 
            WHERE id = %s
            """
            
            cursor.execute(update_sql, (new_type, topic_id))
            print(f"✓ 更新 Topic: {topic_name} -> {new_type}")
        
        conn.commit()
        print("\n✓ Topic 类型更新完成")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"✗ 更新失败：{e}")
        raise


if __name__ == "__main__":
    print("=" * 60)
    print("更新 MQTT Topic 配置类型")
    print("=" * 60)
    print(f"\n数据库：{DB_CONFIG['database']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}\n")
    
    update_topic_types()
    
    print("\n" + "=" * 60)
    print("完成！")
    print("=" * 60)
