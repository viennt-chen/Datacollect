"""
数据库迁移：创建 workshops 和 projects 表
运行方式：python -m app.migrations.create_workshops_projects
"""
from app.database import engine, Base
from app.models.workshop import Workshop
from app.models.project import Project


def create_tables():
    """创建表"""
    try:
        Workshop.__table__.create(engine, checkfirst=True)
        print('[OK] workshops 表创建成功（或已存在）')
    except Exception as e:
        print(f'[ERROR] workshops 表创建失败: {e}')

    try:
        Project.__table__.create(engine, checkfirst=True)
        print('[OK] projects 表创建成功（或已存在）')
    except Exception as e:
        print(f'[ERROR] projects 表创建失败: {e}')


if __name__ == '__main__':
    create_tables()
    print('\n迁移完成')
