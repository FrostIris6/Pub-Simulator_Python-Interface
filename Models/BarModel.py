import json
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database_merge.log"),
        logging.StreamHandler()
    ]
)


class BarModel:
    """酒吧数据模型，处理数据库合并和管理"""

    def __init__(self, source_path="Database/OrderDB.json", target_path="OrderDB.json"):
        self.source_path = source_path
        self.target_path = target_path
        self.product_id_map = {}
        self.next_id = 100

        # 创建目标目录（如果不存在）
        target_dir = os.path.dirname(self.target_path)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            logging.info(f"创建目录: {target_dir}")

        # 创建源目录（如果不存在）
        source_dir = os.path.dirname(self.source_path)
        if source_dir and not os.path.exists(source_dir):
            os.makedirs(source_dir, exist_ok=True)
            logging.info(f"创建目录: {source_dir}")

        # 自动检查并合并数据库
        self.auto_merge_database()

    def auto_merge_database(self):
        """自动检查源数据库是否有更新，如果有则执行合并"""
        try:
            # 检查源文件是否存在
            if not os.path.exists(self.source_path):
                logging.info(f"源数据库文件不存在: {self.source_path}")
                return False

            # 检查源文件和目标文件的修改时间
            source_modified = False
            if os.path.exists(self.target_path):
                source_time = os.path.getmtime(self.source_path)
                target_time = os.path.getmtime(self.target_path)
                source_modified = source_time > target_time

                if not source_modified:
                    logging.info("源数据库未发生变化，不需要合并")
                    return False

            # 执行合并操作
            logging.info("检测到源数据库有更新，开始合并数据...")
            return self.merge_database()
        except Exception as e:
            logging.error(f"自动合并过程中出错: {str(e)}")
            return False

    def merge_database(self):
        """
        将新数据库与现有数据库合并。

        Returns:
            bool: 合并成功返回True，否则返回False
        """
        try:
            # 读取新数据库
            with open(self.source_path, "r", encoding="utf-8") as f:
                try:
                    new_data = json.load(f)
                    logging.info(f"成功加载新数据，来源: {self.source_path}")
                except json.JSONDecodeError as e:
                    logging.error(f"源文件JSON格式无效: {e}")
                    return False

            # 检查数据格式并转换
            transformed_orders = []

            # 如果是单个对象（不在数组中）
            if isinstance(new_data, dict):
                logging.info("源数据是单个订单对象，转换为列表")
                new_data = [new_data]
            elif not isinstance(new_data, list):
                logging.error(f"意外的数据格式: {type(new_data)}. 预期为dict或list")
                return False

            logging.info(f"处理 {len(new_data)} 个新订单...")

            # 加载product_id映射
            self._load_product_id_mapping()

            # 处理每个订单
            for i, order in enumerate(new_data):
                try:
                    # 创建具有预期结构的新订单
                    new_order = {
                        "transaction_id": str(order.get("transaction_id", f"unknown-{i}")),
                        "table_id": str(order.get("table_id", "")),
                        "transaction_time": order.get("transaction_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "breakdown": []
                    }

                    # 处理订单明细
                    if "breakdown" in order and isinstance(order["breakdown"], list):
                        for item in order["breakdown"]:
                            # 获取原始product_id和specification
                            original_product_id = str(item.get("product_id", ""))
                            original_specification = str(item.get("specification", ""))

                            # 合并product_id和specification作为新的specification
                            combined_specification = original_product_id
                            if original_specification:
                                combined_specification += f" - {original_specification}"

                            # 如果有note，添加到specification中
                            if "note" in item and item["note"]:
                                combined_specification += f" ({item['note']})"

                            # 为product_id分配一个数字ID
                            if original_product_id not in self.product_id_map:
                                self.product_id_map[original_product_id] = self.next_id
                                self.next_id += 1

                            numeric_product_id = self.product_id_map[original_product_id]

                            # 创建转换后的商品
                            new_item = {
                                "product_id": numeric_product_id,  # 使用映射的数字ID
                                "price": float(item.get("price", 0)),
                                "amount": int(item.get("amount", 1)),
                                "specification": combined_specification,  # 使用合并后的specification
                                "is_paid": bool(item.get("is_paid", False))
                            }

                            new_order["breakdown"].append(new_item)

                        # 如果没有商品则记录警告
                        if not new_order["breakdown"]:
                            logging.warning(f"订单 {new_order['transaction_id']} 没有商品明细")
                    else:
                        logging.warning(f"订单 {new_order['transaction_id']} 缺少有效的breakdown部分")

                    transformed_orders.append(new_order)
                    logging.info(f"处理订单 {new_order['transaction_id']}，包含 {len(new_order['breakdown'])} 个商品")

                except Exception as e:
                    logging.error(f"处理订单 {i} 时出错: {str(e)}")
                    # 继续处理其他订单

            if not transformed_orders:
                logging.error("没有找到有效的订单进行转换")
                return False

            # 读取现有目标数据库（如果存在）
            existing_orders = self._read_existing_database()

            # 合并现有订单和新订单
            merged_orders = existing_orders + transformed_orders
            logging.info(f"合并后的数据库现在有 {len(merged_orders)} 个订单")

            # 写入合并后的数据到目标路径
            with open(self.target_path, "w", encoding="utf-8") as f:
                json.dump(merged_orders, f, indent=4, ensure_ascii=False)

            # 保存product_id的映射关系
            self._save_product_id_mapping()

            logging.info(f"成功合并 {len(transformed_orders)} 个新订单到数据库")
            logging.info(f"更新后的数据库保存到 {self.target_path}")
            return True

        except Exception as e:
            logging.error(f"数据库合并过程中出错: {str(e)}")
            return False

    def _load_product_id_mapping(self):
        """加载现有的product_id映射"""
        mapping_file = "product_id_mapping.json"
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, "r", encoding="utf-8") as f:
                    self.product_id_map = json.load(f)
                    # 找到最大ID值，确保新ID从最大值之后开始
                    if self.product_id_map:
                        self.next_id = max(self.product_id_map.values()) + 1
                    logging.info(f"已加载现有的产品ID映射，包含 {len(self.product_id_map)} 个项目")
            except Exception as e:
                logging.warning(f"无法加载现有的产品ID映射: {str(e)}")

    def _save_product_id_mapping(self):
        """保存product_id映射到文件"""
        mapping_file = "product_id_mapping.json"
        try:
            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(self.product_id_map, f, indent=4, ensure_ascii=False)
                logging.info(f"产品ID映射已保存到 {mapping_file}")
        except Exception as e:
            logging.error(f"保存产品ID映射时出错: {str(e)}")

    def _read_existing_database(self):
        """读取现有数据库"""
        existing_orders = []
        if os.path.exists(self.target_path):
            try:
                with open(self.target_path, "r", encoding="utf-8") as f:
                    existing_orders = json.load(f)
                    if not isinstance(existing_orders, list):
                        existing_orders = []
                    logging.info(f"从 {self.target_path} 加载了 {len(existing_orders)} 个现有订单")
            except Exception as e:
                logging.warning(f"无法加载现有数据库，将创建新数据库: {str(e)}")
        return existing_orders

    def validate_database(self):
        """
        验证数据库确保其符合预期格式。

        Returns:
            bool: 验证通过返回True，否则返回False
        """
        try:
            with open(self.target_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                logging.error("验证失败: 根数据不是数组")
                return False

            for i, order in enumerate(data):
                # 检查必填字段
                required_fields = ["transaction_id", "table_id", "transaction_time", "breakdown"]
                for field in required_fields:
                    if field not in order:
                        logging.error(f"验证失败: 订单 {i} 缺少必填字段 '{field}'")
                        return False

                # 验证breakdown
                if not isinstance(order["breakdown"], list):
                    logging.error(f"验证失败: 订单 {i} 的breakdown不是数组")
                    return False

                for j, item in enumerate(order["breakdown"]):
                    # 检查必填项字段
                    item_fields = ["product_id", "price", "amount", "specification"]
                    for field in item_fields:
                        if field not in item:
                            logging.error(f"验证失败: 订单 {i} 中的商品 {j} 缺少字段 '{field}'")
                            return False

            logging.info(f"验证通过，共 {len(data)} 个订单")
            return True

        except Exception as e:
            logging.error(f"验证错误: {str(e)}")
            return False


# 独立运行时的测试代码
if __name__ == "__main__":
    print("BarModel测试")
    print("===========")

    model = BarModel()
    print("自动合并数据库操作完成")

    print("验证数据库...")
    if model.validate_database():
        print("验证通过。数据库已准备好供应用程序使用。")
    else:
        print("验证失败。请查看日志文件以获取详细信息。")