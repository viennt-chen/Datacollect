"""
U9 服务类
功能：封装 U9 ERP 系统的 API 调用（异步版本）
"""
import aiohttp
import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from functools import wraps

logger = logging.getLogger(__name__)


class U9ServiceError(Exception):
    """U9 服务异常基类"""
    def __init__(self, message: str, error_type: str = "U9_SERVICE_ERROR"):
        super().__init__(message)
        self.error_type = error_type


class U9NetworkError(U9ServiceError):
    """U9 网络请求异常"""
    def __init__(self, message: str):
        super().__init__(message, "U9_NETWORK_ERROR")


class U9DataError(U9ServiceError):
    """U9 数据格式异常"""
    def __init__(self, message: str):
        super().__init__(message, "U9_DATA_ERROR")


class U9TimeoutError(U9ServiceError):
    """U9 请求超时异常"""
    def __init__(self, message: str):
        super().__init__(message, "U9_TIMEOUT_ERROR")


def safe_u9_call_async(func):
    """
    装饰器：安全调用 U9 接口（异步版本），捕获所有异常并返回默认值
    防止 U9 接口异常影响主程序
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except U9ServiceError:
            raise
        except asyncio.TimeoutError as e:
            logger.error(f"U9 接口调用超时 [{func.__name__}]: {e}")
            raise U9TimeoutError(f"U9 接口调用超时: {str(e)}")
        except aiohttp.ClientConnectionError as e:
            logger.error(f"U9 接口连接失败 [{func.__name__}]: {e}")
            raise U9NetworkError(f"U9 接口连接失败: {str(e)}")
        except aiohttp.ClientError as e:
            logger.error(f"U9 接口网络请求失败 [{func.__name__}]: {e}")
            raise U9NetworkError(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"U9 接口 JSON 解析失败 [{func.__name__}]: {e}")
            raise U9DataError(f"JSON 解析失败: {str(e)}")
        except Exception as e:
            logger.error(f"U9 接口调用未知异常 [{func.__name__}]: {e}", exc_info=True)
            raise U9ServiceError(f"U9 接口调用异常: {str(e)}")
    
    return wrapper


class U9Service:
    """U9 ERP 系统服务类（异步版本）"""
    
    U9_API_URL = "https://erp.jsxq.group/U9/RestServices/COM.XQ.WMS.IQryWMSMO.svc/Do"
    
    @staticmethod
    @safe_u9_call_async
    async def query_mo_orders_async(specs: str, start_date: str, end_date: str, item_code: str = "") -> List[Dict[str, Any]]:
        """
        查询制造订单数据（异步版本）
        
        Args:
            specs: 规格型号
            start_date: 开始日期
            end_date: 结束日期
            item_code: U9 物料号（可选，优先使用 itemCode 查询）
            
        Returns:
            订单数据列表
        """
        params = {
            "context": {
                "CultureName": "zh-CN",
                "EntCode": "001",
                "OrgCode": "28",
                "UserCode": "shsbhyz"
            }, 
            "startDate": start_date,
            "endDate": end_date,
            "docType": "DMO",
            "itemCode": item_code,
            "dept": "",
            "specs": specs
        }
        
        headers = {"Content-Type": "application/json"}
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(U9Service.U9_API_URL, json=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
        
        if not data.get('d'):
            return []
        
        if 'd' in data:
            outer_data = data['d']
            if not outer_data:
                return []
                
            cleaned_data = outer_data.replace('\r\n', '\n').replace('\\r\\n', '\\n').replace('\\\\', '\\')
            parsed_data = json.loads(cleaned_data)
            
            if 'msg' in parsed_data:
                msg_data = parsed_data['msg']
                
                if not msg_data:
                    return []
                
                try:
                    if isinstance(msg_data, str):
                        msg_data = json.loads(msg_data)
                except:
                    pass
                
                if isinstance(msg_data, list) and len(msg_data) > 0:
                    return msg_data
                else:
                    return []
            else:
                raise U9DataError("U9 接口返回数据格式错误: 缺少 msg 字段")
        else:
            raise U9DataError("U9 接口返回数据格式错误: 缺少 d 字段")
    
    @staticmethod
    @safe_u9_call_async
    async def get_planned_output_async(specs: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        获取计划总产量（异步版本）
        
        Args:
            specs: 规格型号
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            计划产量数据
        """
        today = datetime.now().strftime('%Y-%m-%d')
        query_start_date = start_date if start_date else today
        query_end_date = end_date if end_date else today
        
        params = {
            "context": {
                "CultureName": "zh-CN",
                "EntCode": "001",
                "OrgCode": "28",
                "UserCode": "shsbhyz"
            }, 
            "startDate": query_start_date,
            "endDate": query_end_date,
            "docType": "DMO",
            "itemCode": "",
            "dept": "",
            "specs": specs
        }
        
        headers = {"Content-Type": "application/json"}
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(U9Service.U9_API_URL, json=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
        
        if not data.get('d'):
            return {
                "planned_output": 0,
                "specs": specs,
                "date": today,
                "details": []
            }
        
        if 'd' in data:
            outer_data = data['d']
            if not outer_data:
                return {
                    "planned_output": 0,
                    "specs": specs,
                    "date": today,
                    "details": []
                }
                
            cleaned_data = outer_data.replace('\r\n', '\n').replace('\\r\\n', '\\n').replace('\\\\', '\\')
            parsed_data = json.loads(cleaned_data)
            
            if 'msg' in parsed_data:
                msg_data = parsed_data['msg']
                
                if not msg_data:
                    return {
                        "planned_output": 0,
                        "specs": specs,
                        "date": today,
                        "details": []
                    }
                
                try:
                    if isinstance(msg_data, str):
                        msg_data = json.loads(msg_data)
                except:
                    pass
                
                if isinstance(msg_data, list) and len(msg_data) > 0:
                    planned_output = msg_data[0].get('productQty', 0) if msg_data else 0
                    
                    return {
                        "planned_output": planned_output,
                        "specs": specs,
                        "date": today,
                        "details": msg_data
                    }
                else:
                    return {
                        "planned_output": 0,
                        "specs": specs,
                        "date": today,
                        "details": []
                    }
            else:
                raise U9DataError("U9 接口返回数据格式错误: 缺少 msg 字段")
        else:
            raise U9DataError("U9 接口返回数据格式错误: 缺少 d 字段")
    
    @staticmethod
    async def query_mo_orders(specs: str, start_date: str, end_date: str, item_code: str = "") -> List[Dict[str, Any]]:
        """查询制造订单数据（向后兼容的同步接口，实际调用异步版本）"""
        return await U9Service.query_mo_orders_async(specs, start_date, end_date, item_code)
    
    @staticmethod
    async def get_planned_output(specs: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """获取计划总产量（向后兼容的同步接口，实际调用异步版本）"""
        return await U9Service.get_planned_output_async(specs, start_date, end_date)