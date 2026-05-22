"""
产品订单防重复写入机制测试脚本
测试各种可能导致重复写入的异常场景
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import asyncio

from app.models.product_order import ProductOrder, ProductOrderDetail
from app.routers.erp_orders import save_order_to_db_with_upsert


# 测试数据库配置
TEST_DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/kp3_test"


def create_test_engine():
    """创建测试数据库引擎"""
    engine = create_engine(TEST_DATABASE_URL, echo=False)
    return engine


def test_duplicate_prevention():
    """测试防重复写入机制"""
    print("\n" + "=" * 80)
    print("测试 1: 防重复写入机制")
    print("=" * 80)
    
    engine = create_test_engine()
    Session = sessionmaker(bind=engine)
    
    # 测试数据
    test_data = {
        'planned_output': 1000,
        'details': [
            {
                'docNo': 'TEST-DMO-001',
                'itemCode': 'TEST-ITEM-001',
                'specs': 'Test Spec',
                'itemName': 'Test Item',
                'productQty': 500,
                'totalCompleteQty': 200,
                'totalEligibleQty': 200,
                'totalScrapQty': 0,
                'completeWh': 'Test Warehouse',
                'completeWhCode': 'WH01',
                'docTypeCode': 'DMO',
                'docType': '生产订单',
                'docState': '开工',
                'project': 'Test Project',
                'departmentCode': 'DEPT01',
                'departmentName': 'Test Department'
            },
            {
                'docNo': 'TEST-DMO-002',
                'itemCode': 'TEST-ITEM-001',
                'specs': 'Test Spec',
                'itemName': 'Test Item',
                'productQty': 500,
                'totalCompleteQty': 300,
                'totalEligibleQty': 300,
                'totalScrapQty': 0,
                'completeWh': 'Test Warehouse',
                'completeWhCode': 'WH01',
                'docTypeCode': 'DMO',
                'docType': '生产订单',
                'docState': '完工',
                'project': 'Test Project',
                'departmentCode': 'DEPT01',
                'departmentName': 'Test Department'
            }
        ]
    }
    
    query_date = datetime.now().strftime('%Y-%m-%d')
    
    # 第一次写入
    print("\n[步骤 1] 第一次写入订单数据...")
    db = Session()
    try:
        count1 = asyncio.run(save_order_to_db_with_upsert(
            db=db,
            part_number='TEST-PART-001',
            u9_material_code='TEST-MATERIAL-001',
            specs='Test Specification',
            order_data=test_data,
            query_date=query_date
        ))
        print(f"  ✓ 第一次写入成功，保存 {count1} 条明细记录")
        
        # 验证数据库中的记录数
        order = db.query(ProductOrder).filter(
            ProductOrder.u9_material_code == 'TEST-MATERIAL-001',
            ProductOrder.query_date == query_date
        ).first()
        
        if order:
            detail_count = db.query(ProductOrderDetail).filter(
                ProductOrderDetail.order_id == order.id
            ).count()
            print(f"  ✓ 数据库中明细记录数: {detail_count}")
        
        db.commit()
    except Exception as e:
        print(f"  ✗ 第一次写入失败: {e}")
        db.rollback()
    finally:
        db.close()
    
    # 第二次写入（相同数据，模拟重复执行）
    print("\n[步骤 2] 第二次写入相同订单数据（模拟重复执行）...")
    db = Session()
    try:
        count2 = asyncio.run(save_order_to_db_with_upsert(
            db=db,
            part_number='TEST-PART-001',
            u9_material_code='TEST-MATERIAL-001',
            specs='Test Specification',
            order_data=test_data,
            query_date=query_date
        ))
        print(f"  ✓ 第二次写入成功，保存 {count2} 条明细记录")
        
        # 验证数据库中的记录数（应该与第一次相同）
        order = db.query(ProductOrder).filter(
            ProductOrder.u9_material_code == 'TEST-MATERIAL-001',
            ProductOrder.query_date == query_date
        ).first()
        
        if order:
            detail_count = db.query(ProductOrderDetail).filter(
                ProductOrderDetail.order_id == order.id
            ).count()
            print(f"  ✓ 数据库中明细记录数: {detail_count}")
            
            if detail_count == count1:
                print(f"  ✓ 防重复机制有效：记录数未增加")
            else:
                print(f"  ✗ 防重复机制失效：记录数从 {count1} 增加到 {detail_count}")
        
        # 验证主表记录数（应该只有 1 条）
        main_count = db.query(ProductOrder).filter(
            ProductOrder.u9_material_code == 'TEST-MATERIAL-001',
            ProductOrder.query_date == query_date
        ).count()
        print(f"  ✓ 主表记录数: {main_count}")
        
        if main_count == 1:
            print(f"  ✓ 主表防重复机制有效")
        else:
            print(f"  ✗ 主表防重复机制失效")
        
        db.commit()
    except Exception as e:
        print(f"  ✗ 第二次写入失败: {e}")
        db.rollback()
    finally:
        db.close()
    
    # 第三次写入（更新数据）
    print("\n[步骤 3] 第三次写入（更新订单数据）...")
    updated_data = {
        'planned_output': 1500,
        'details': [
            {
                'docNo': 'TEST-DMO-001',
                'itemCode': 'TEST-ITEM-001',
                'specs': 'Test Spec Updated',
                'itemName': 'Test Item Updated',
                'productQty': 800,
                'totalCompleteQty': 400,
                'totalEligibleQty': 400,
                'totalScrapQty': 0,
                'completeWh': 'Test Warehouse Updated',
                'completeWhCode': 'WH02',
                'docTypeCode': 'DMO',
                'docType': '生产订单',
                'docState': '已关闭',
                'project': 'Test Project Updated',
                'departmentCode': 'DEPT02',
                'departmentName': 'Test Department Updated'
            },
            {
                'docNo': 'TEST-DMO-002',
                'itemCode': 'TEST-ITEM-001',
                'specs': 'Test Spec Updated',
                'itemName': 'Test Item Updated',
                'productQty': 700,
                'totalCompleteQty': 500,
                'totalEligibleQty': 500,
                'totalScrapQty': 0,
                'completeWh': 'Test Warehouse Updated',
                'completeWhCode': 'WH02',
                'docTypeCode': 'DMO',
                'docType': '生产订单',
                'docState': '已关闭',
                'project': 'Test Project Updated',
                'departmentCode': 'DEPT02',
                'departmentName': 'Test Department Updated'
            },
            {
                'docNo': 'TEST-DMO-003',
                'itemCode': 'TEST-ITEM-001',
                'specs': 'Test Spec New',
                'itemName': 'Test Item New',
                'productQty': 300,
                'totalCompleteQty': 100,
                'totalEligibleQty': 100,
                'totalScrapQty': 0,
                'completeWh': 'New Warehouse',
                'completeWhCode': 'WH03',
                'docTypeCode': 'DMO',
                'docType': '生产订单',
                'docState': '开工',
                'project': 'New Project',
                'departmentCode': 'DEPT03',
                'departmentName': 'New Department'
            }
        ]
    }
    
    db = Session()
    try:
        count3 = asyncio.run(save_order_to_db_with_upsert(
            db=db,
            part_number='TEST-PART-001',
            u9_material_code='TEST-MATERIAL-001',
            specs='Test Specification',
            order_data=updated_data,
            query_date=query_date
        ))
        print(f"  ✓ 第三次写入成功，保存 {count3} 条明细记录")
        
        # 验证数据已更新
        order = db.query(ProductOrder).filter(
            ProductOrder.u9_material_code == 'TEST-MATERIAL-001',
            ProductOrder.query_date == query_date
        ).first()
        
        if order:
            print(f"  ✓ 计划总产量已更新: {order.planned_output}")
            
            detail_count = db.query(ProductOrderDetail).filter(
                ProductOrderDetail.order_id == order.id
            ).count()
            print(f"  ✓ 数据库中明细记录数: {detail_count}")
            
            if detail_count == 3:
                print(f"  ✓ 更新机制有效：新增订单号已写入")
            else:
                print(f"  ✗ 更新机制可能有问题")
            
            # 验证订单号 001 的数据已更新
            detail_001 = db.query(ProductOrderDetail).filter(
                ProductOrderDetail.order_id == order.id,
                ProductOrderDetail.doc_no == 'TEST-DMO-001'
            ).first()
            
            if detail_001:
                print(f"  ✓ 订单号 TEST-DMO-001 已更新:")
                print(f"    - product_qty: {detail_001.product_qty}")
                print(f"    - doc_state: {detail_001.doc_state}")
        
        db.commit()
    except Exception as e:
        print(f"  ✗ 第三次写入失败: {e}")
        db.rollback()
    finally:
        db.close()


def test_batch_duplicate_prevention():
    """测试批次内重复订单号防护"""
    print("\n" + "=" * 80)
    print("测试 2: 批次内重复订单号防护")
    print("=" * 80)
    
    engine = create_test_engine()
    Session = sessionmaker(bind=engine)
    
    # 测试数据：包含重复订单号
    test_data_with_duplicates = {
        'planned_output': 2000,
        'details': [
            {
                'docNo': 'TEST-DUP-001',
                'itemCode': 'TEST-ITEM-002',
                'specs': 'Test Spec',
                'itemName': 'Test Item',
                'productQty': 500,
                'totalCompleteQty': 200,
                'totalEligibleQty': 200,
                'totalScrapQty': 0,
                'completeWh': 'Test Warehouse',
                'completeWhCode': 'WH01',
                'docTypeCode': 'DMO',
                'docType': '生产订单',
                'docState': '开工',
                'project': 'Test Project',
                'departmentCode': 'DEPT01',
                'departmentName': 'Test Department'
            },
            {
                'docNo': 'TEST-DUP-001',  # 重复订单号
                'itemCode': 'TEST-ITEM-002',
                'specs': 'Test Spec Duplicate',
                'itemName': 'Test Item Duplicate',
                'productQty': 1000,
                'totalCompleteQty': 500,
                'totalEligibleQty': 500,
                'totalScrapQty': 0,
                'completeWh': 'Test Warehouse',
                'completeWhCode': 'WH01',
                'docTypeCode': 'DMO',
                'docType': '生产订单',
                'docState': '开工',
                'project': 'Test Project',
                'departmentCode': 'DEPT01',
                'departmentName': 'Test Department'
            },
            {
                'docNo': 'TEST-DUP-002',
                'itemCode': 'TEST-ITEM-002',
                'specs': 'Test Spec',
                'itemName': 'Test Item',
                'productQty': 500,
                'totalCompleteQty': 300,
                'totalEligibleQty': 300,
                'totalScrapQty': 0,
                'completeWh': 'Test Warehouse',
                'completeWhCode': 'WH01',
                'docTypeCode': 'DMO',
                'docType': '生产订单',
                'docState': '完工',
                'project': 'Test Project',
                'departmentCode': 'DEPT01',
                'departmentName': 'Test Department'
            }
        ]
    }
    
    query_date = datetime.now().strftime('%Y-%m-%d')
    
    print("\n[步骤] 写入包含重复订单号的数据...")
    db = Session()
    try:
        count = asyncio.run(save_order_to_db_with_upsert(
            db=db,
            part_number='TEST-PART-002',
            u9_material_code='TEST-MATERIAL-002',
            specs='Test Specification',
            order_data=test_data_with_duplicates,
            query_date=query_date
        ))
        print(f"  ✓ 写入成功，保存 {count} 条明细记录")
        
        # 验证数据库中的记录数（应该只有 2 条，重复的已过滤）
        order = db.query(ProductOrder).filter(
            ProductOrder.u9_material_code == 'TEST-MATERIAL-002',
            ProductOrder.query_date == query_date
        ).first()
        
        if order:
            detail_count = db.query(ProductOrderDetail).filter(
                ProductOrderDetail.order_id == order.id
            ).count()
            print(f"  ✓ 数据库中明细记录数: {detail_count}")
            
            if detail_count == 2:
                print(f"  ✓ 批次内重复防护有效：重复订单号已过滤")
            else:
                print(f"  ✗ 批次内重复防护失效")
        
        db.commit()
    except Exception as e:
        print(f"  ✗ 写入失败: {e}")
        db.rollback()
    finally:
        db.close()


def cleanup_test_data():
    """清理测试数据"""
    print("\n" + "=" * 80)
    print("清理测试数据")
    print("=" * 80)
    
    engine = create_test_engine()
    Session = sessionmaker(bind=engine)
    db = Session()
    
    try:
        query_date = datetime.now().strftime('%Y-%m-%d')
        
        # 删除测试订单
        test_materials = ['TEST-MATERIAL-001', 'TEST-MATERIAL-002']
        
        for material in test_materials:
            order = db.query(ProductOrder).filter(
                ProductOrder.u9_material_code == material,
                ProductOrder.query_date == query_date
            ).first()
            
            if order:
                # 删除明细
                db.query(ProductOrderDetail).filter(
                    ProductOrderDetail.order_id == order.id
                ).delete()
                
                # 删除主表
                db.delete(order)
        
        db.commit()
        print("  ✓ 测试数据清理完成")
        
    except Exception as e:
        print(f"  ✗ 清理失败: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("产品订单防重复写入机制测试")
    print("=" * 80)
    
    try:
        # 运行测试
        test_duplicate_prevention()
        test_batch_duplicate_prevention()
        
        print("\n" + "=" * 80)
        print("所有测试完成")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 清理测试数据
        cleanup_test_data()
