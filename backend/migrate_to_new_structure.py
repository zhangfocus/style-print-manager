"""
数据迁移脚本：将旧表结构迁移到新表结构
旧结构：rule_type(字符串), style_id, position_id, print_id, allowed_print_ids, allowed_style_ids
新结构：rule_type(整数), position_id, style_ids, print_ids
"""
import sys
sys.path.insert(0, '.')

from app.database import engine
from sqlalchemy import text

def migrate_data():
    with engine.connect() as conn:
        print("开始数据迁移...")

        # 1. 删除旧表（如果存在新表）
        print("\n1. 删除旧的 style_position_rules 表...")
        conn.execute(text("DROP TABLE IF EXISTS style_position_rules"))
        conn.commit()

        # 2. 创建新表结构
        print("\n2. 创建新表结构...")
        create_table_sql = """
        CREATE TABLE style_position_rules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            rule_type INT NOT NULL COMMENT '规则类型: 3=style_position, 2=position_restriction, 1=style_ban',
            position_id INT NULL COMMENT '位置ID',
            style_ids TEXT NULL COMMENT '款式ID(逗号分隔)',
            print_ids TEXT NULL COMMENT '印花ID(逗号分隔)',
            is_active TINYINT(1) DEFAULT 1 COMMENT '是否启用',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

            INDEX idx_rule_type_position (rule_type, position_id),
            UNIQUE KEY uq_rule_position_styles_prints (rule_type, position_id, style_ids(255), print_ids(255)),

            FOREIGN KEY (position_id) REFERENCES positions(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        """
        conn.execute(text(create_table_sql))
        conn.commit()

        # 3. 迁移数据
        print("\n3. 迁移数据...")

        # 3.1 迁移类型1：style_ban
        print("  - 迁移 style_ban 规则...")
        migrate_style_ban = """
        INSERT INTO style_position_rules (rule_type, position_id, style_ids, print_ids, is_active, created_at, updated_at)
        SELECT
            1 as rule_type,
            NULL as position_id,
            CAST(style_id AS CHAR) as style_ids,
            NULL as print_ids,
            is_active,
            created_at,
            updated_at
        FROM style_position_rules_old
        WHERE rule_type = 'style_ban' AND style_id IS NOT NULL
        """
        result = conn.execute(text(migrate_style_ban))
        print(f"    迁移了 {result.rowcount} 条 style_ban 规则")
        conn.commit()

        # 3.2 迁移类型2：position_restriction
        print("  - 迁移 position_restriction 规则...")
        migrate_position_restriction = """
        INSERT INTO style_position_rules (rule_type, position_id, style_ids, print_ids, is_active, created_at, updated_at)
        SELECT
            2 as rule_type,
            position_id,
            allowed_style_ids as style_ids,
            allowed_print_ids as print_ids,
            is_active,
            created_at,
            updated_at
        FROM style_position_rules_old
        WHERE rule_type = 'position_restriction'
            AND position_id IS NOT NULL
            AND allowed_style_ids IS NOT NULL
            AND allowed_print_ids IS NOT NULL
        """
        result = conn.execute(text(migrate_position_restriction))
        print(f"    迁移了 {result.rowcount} 条 position_restriction 规则")
        conn.commit()

        # 3.3 迁移类型3：style_position
        print("  - 迁移 style_position 规则...")
        migrate_style_position = """
        INSERT INTO style_position_rules (rule_type, position_id, style_ids, print_ids, is_active, created_at, updated_at)
        SELECT
            3 as rule_type,
            position_id,
            CAST(style_id AS CHAR) as style_ids,
            allowed_print_ids as print_ids,
            is_active,
            created_at,
            updated_at
        FROM style_position_rules_old
        WHERE rule_type = 'style_position'
            AND style_id IS NOT NULL
            AND position_id IS NOT NULL
        """
        result = conn.execute(text(migrate_style_position))
        print(f"    迁移了 {result.rowcount} 条 style_position 规则")
        conn.commit()

        # 4. 验证迁移结果
        print("\n4. 验证迁移结果...")
        result = conn.execute(text("""
            SELECT rule_type, COUNT(*) as cnt
            FROM style_position_rules
            GROUP BY rule_type
            ORDER BY rule_type
        """))

        print("\n新表数据统计：")
        total = 0
        for row in result:
            type_name = {1: 'style_ban', 2: 'position_restriction', 3: 'style_position'}.get(row[0], 'unknown')
            print(f"  rule_type={row[0]} ({type_name}): {row[1]} 条")
            total += row[1]

        print(f"\n总计: {total} 条")

        # 5. 对比旧表数据量
        result = conn.execute(text("SELECT COUNT(*) FROM style_position_rules_old"))
        old_count = result.scalar()
        print(f"旧表数据量: {old_count} 条")

        if total == old_count:
            print("\n✓ 数据迁移成功！数据量一致。")
        else:
            print(f"\n⚠ 警告：数据量不一致！旧表 {old_count} 条，新表 {total} 条")

        print("\n迁移完成！")
        print("注意：旧表 style_position_rules_old 已保留，如需删除请手动执行：")
        print("  DROP TABLE style_position_rules_old;")

if __name__ == "__main__":
    try:
        migrate_data()
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
