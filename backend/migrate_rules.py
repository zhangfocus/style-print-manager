"""
数据库迁移脚本：重构限定规则表
1. 删除 print_restriction 和 position_print 类型的规则
2. 添加 print_id 外键列
3. 删除 print_code、allowed_prints、allowed_styles、allowed_style_positions 列
4. 添加 allowed_print_ids、allowed_style_ids 列
"""
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:123456@localhost:3306/style_print_manager?charset=utf8mb4")
engine = create_engine(DATABASE_URL)

def migrate():
    with engine.connect() as conn:
        print("开始数据库迁移...")

        # 1. 删除旧的规则类型
        print("\n1. 删除 print_restriction 和 position_print 规则...")
        result = conn.execute(text("""
            DELETE FROM style_position_rules
            WHERE rule_type IN ('print_restriction', 'position_print')
        """))
        conn.commit()
        print(f"   删除了 {result.rowcount} 条规则")

        # 2. 添加新列
        print("\n2. 添加新列...")
        try:
            conn.execute(text("""
                ALTER TABLE style_position_rules
                ADD COLUMN print_id INT NULL COMMENT '印花ID' AFTER position_id
            """))
            conn.commit()
            print("   添加 print_id 列成功")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("   print_id 列已存在，跳过")
            else:
                raise

        try:
            conn.execute(text("""
                ALTER TABLE style_position_rules
                ADD COLUMN allowed_print_ids TEXT NULL COMMENT '允许印花ID(逗号分隔)' AFTER print_id
            """))
            conn.commit()
            print("   添加 allowed_print_ids 列成功")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("   allowed_print_ids 列已存在，跳过")
            else:
                raise

        try:
            conn.execute(text("""
                ALTER TABLE style_position_rules
                ADD COLUMN allowed_style_ids TEXT NULL COMMENT '允许款式ID(逗号分隔)' AFTER allowed_print_ids
            """))
            conn.commit()
            print("   添加 allowed_style_ids 列成功")
        except Exception as e:
            if "Duplicate column" in str(e):
                print("   allowed_style_ids 列已存在，跳过")
            else:
                raise

        # 3. 添加外键约束
        print("\n3. 添加外键约束...")
        try:
            conn.execute(text("""
                ALTER TABLE style_position_rules
                ADD CONSTRAINT fk_print_id
                FOREIGN KEY (print_id) REFERENCES prints(id) ON DELETE CASCADE
            """))
            conn.commit()
            print("   添加 print_id 外键成功")
        except Exception as e:
            if "Duplicate" in str(e) or "already exists" in str(e):
                print("   print_id 外键已存在，跳过")
            else:
                raise

        # 4. 删除旧列
        print("\n4. 删除旧列...")
        old_columns = ['print_code', 'allowed_prints', 'allowed_styles', 'allowed_style_positions']
        for col in old_columns:
            try:
                conn.execute(text(f"ALTER TABLE style_position_rules DROP COLUMN {col}"))
                conn.commit()
                print(f"   删除 {col} 列成功")
            except Exception as e:
                if "doesn't exist" in str(e) or "Unknown column" in str(e):
                    print(f"   {col} 列不存在，跳过")
                else:
                    raise

        print("\n✓ 数据库迁移完成！")

if __name__ == "__main__":
    migrate()
