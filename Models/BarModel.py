import json
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("database_merge.log"),
        logging.StreamHandler()
    ]
)


class BarModel:
    """Bar data model, handles database merging and management"""

    def __init__(self, source_path="Database/OrderDB.json", target_path="OrderDB.json"):
        self.source_path = source_path
        self.target_path = target_path
        self.product_id_map = {}
        self.next_id = 100

        # Create target directory (if it doesn't exist)
        target_dir = os.path.dirname(self.target_path)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir, exist_ok=True)
            logging.info(f"Created directory: {target_dir}")

        # Create source directory (if it doesn't exist)
        source_dir = os.path.dirname(self.source_path)
        if source_dir and not os.path.exists(source_dir):
            os.makedirs(source_dir, exist_ok=True)
            logging.info(f"Created directory: {source_dir}")

        # Automatically check and merge database
        self.auto_merge_database()

    def auto_merge_database(self):
        """Automatically check if source database has updates, if so, perform merge"""
        try:
            # Check if source file exists
            if not os.path.exists(self.source_path):
                logging.info(f"Source database file does not exist: {self.source_path}")
                return False

            # Check modification times of source and target files
            source_modified = False
            if os.path.exists(self.target_path):
                source_time = os.path.getmtime(self.source_path)
                target_time = os.path.getmtime(self.target_path)
                source_modified = source_time > target_time

                if not source_modified:
                    logging.info("Source database has not changed, no need to merge")
                    return False

            # Perform merge operation
            logging.info("Detected updates in source database, starting merge...")
            return self.merge_database()
        except Exception as e:
            logging.error(f"Error during automatic merge process: {str(e)}")
            return False

    def merge_database(self):
        """
        Merge new database with existing database.

        Returns:
            bool: True if merge successful, False otherwise
        """
        try:
            # Read new database
            with open(self.source_path, "r", encoding="utf-8") as f:
                try:
                    new_data = json.load(f)
                    logging.info(f"Successfully loaded new data from: {self.source_path}")
                except json.JSONDecodeError as e:
                    logging.error(f"Source file has invalid JSON format: {e}")
                    return False

            # Check data format and transform
            transformed_orders = []

            # If it's a single object (not in an array)
            if isinstance(new_data, dict):
                logging.info("Source data is a single order object, converting to list")
                new_data = [new_data]
            elif not isinstance(new_data, list):
                logging.error(f"Unexpected data format: {type(new_data)}. Expected dict or list")
                return False

            logging.info(f"Processing {len(new_data)} new orders...")

            # Load product_id mapping
            self._load_product_id_mapping()

            # Process each order
            for i, order in enumerate(new_data):
                try:
                    # Create new order with expected structure
                    new_order = {
                        "transaction_id": str(order.get("transaction_id", f"unknown-{i}")),
                        "table_id": str(order.get("table_id", "")),
                        "transaction_time": order.get("transaction_time", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                        "breakdown": []
                    }

                    # Process order details
                    if "breakdown" in order and isinstance(order["breakdown"], list):
                        for item in order["breakdown"]:
                            # Get original product_id and specification
                            original_product_id = str(item.get("product_id", ""))
                            original_specification = str(item.get("specification", ""))

                            # Merge product_id and specification as new specification
                            combined_specification = original_product_id
                            if original_specification:
                                combined_specification += f" - {original_specification}"

                            # If there's a note, add it to specification
                            if "notes" in item and item["notes"]:
                                combined_specification += f" ({item['notes']})"

                            # Assign a numeric ID for product_id
                            if original_product_id not in self.product_id_map:
                                self.product_id_map[original_product_id] = self.next_id
                                self.next_id += 1

                            numeric_product_id = self.product_id_map[original_product_id]

                            # Create transformed product
                            new_item = {
                                "product_id": numeric_product_id,  # Use mapped numeric ID
                                "price": float(item.get("price", 0)),
                                "amount": int(item.get("amount", 1)),
                                "specification": combined_specification,  # Use combined specification
                                "is_paid": bool(item.get("is_paid", False))
                            }

                            new_order["breakdown"].append(new_item)

                        # Log warning if no products
                        if not new_order["breakdown"]:
                            logging.warning(f"Order {new_order['transaction_id']} has no product details")
                    else:
                        logging.warning(f"Order {new_order['transaction_id']} is missing valid breakdown section")

                    transformed_orders.append(new_order)
                    logging.info(f"Processed order {new_order['transaction_id']}, containing {len(new_order['breakdown'])} products")

                except Exception as e:
                    logging.error(f"Error processing order {i}: {str(e)}")
                    # Continue processing other orders

            if not transformed_orders:
                logging.error("No valid orders found for conversion")
                return False

            # Read existing target database (if it exists)
            existing_orders = self._read_existing_database()

            # Merge existing orders and new orders
            merged_orders = existing_orders + transformed_orders
            logging.info(f"Merged database now has {len(merged_orders)} orders")

            # Write merged data to target path
            with open(self.target_path, "w", encoding="utf-8") as f:
                json.dump(merged_orders, f, indent=4, ensure_ascii=False)

            # Save product_id mapping
            self._save_product_id_mapping()

            logging.info(f"Successfully merged {len(transformed_orders)} new orders to database")
            logging.info(f"Updated database saved to {self.target_path}")
            return True

        except Exception as e:
            logging.error(f"Error during database merge process: {str(e)}")
            return False

    def _load_product_id_mapping(self):
        """Load existing product_id mapping"""
        mapping_file = "product_id_mapping.json"
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, "r", encoding="utf-8") as f:
                    self.product_id_map = json.load(f)
                    # Find maximum ID value, ensure new IDs start after max value
                    if self.product_id_map:
                        self.next_id = max(self.product_id_map.values()) + 1
                    logging.info(f"Loaded existing product ID mapping, containing {len(self.product_id_map)} items")
            except Exception as e:
                logging.warning(f"Unable to load existing product ID mapping: {str(e)}")

    def _save_product_id_mapping(self):
        """Save product_id mapping to file"""
        mapping_file = "product_id_mapping.json"
        try:
            with open(mapping_file, "w", encoding="utf-8") as f:
                json.dump(self.product_id_map, f, indent=4, ensure_ascii=False)
                logging.info(f"Product ID mapping saved to {mapping_file}")
        except Exception as e:
            logging.error(f"Error saving product ID mapping: {str(e)}")

    def _read_existing_database(self):
        """Read existing database"""
        existing_orders = []
        if os.path.exists(self.target_path):
            try:
                with open(self.target_path, "r", encoding="utf-8") as f:
                    existing_orders = json.load(f)
                    if not isinstance(existing_orders, list):
                        existing_orders = []
                    logging.info(f"Loaded {len(existing_orders)} existing orders from {self.target_path}")
            except Exception as e:
                logging.warning(f"Unable to load existing database, will create new database: {str(e)}")
        return existing_orders

    def validate_database(self):
        """
        Validate database to ensure it conforms to expected format.

        Returns:
            bool: True if validation passes, False otherwise
        """
        try:
            with open(self.target_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not isinstance(data, list):
                logging.error("Validation failed: Root data is not an array")
                return False

            for i, order in enumerate(data):
                # Check required fields
                required_fields = ["transaction_id", "table_id", "transaction_time", "breakdown"]
                for field in required_fields:
                    if field not in order:
                        logging.error(f"Validation failed: Order {i} is missing required field '{field}'")
                        return False

                # Validate breakdown
                if not isinstance(order["breakdown"], list):
                    logging.error(f"Validation failed: Order {i}'s breakdown is not an array")
                    return False

                for j, item in enumerate(order["breakdown"]):
                    # Check required item fields
                    item_fields = ["product_id", "price", "amount", "specification"]
                    for field in item_fields:
                        if field not in item:
                            logging.error(f"Validation failed: Product {j} in order {i} is missing field '{field}'")
                            return False

            logging.info(f"Validation passed, {len(data)} orders total")
            return True

        except Exception as e:
            logging.error(f"Validation error: {str(e)}")
            return False


# Test code for independent run
if __name__ == "__main__":
    print("BarModel Test")
    print("===========")

    model = BarModel()
    print("Auto database merge operation completed")

    print("Validating database...")
    if model.validate_database():
        print("Validation passed. Database is ready for application use.")
    else:
        print("Validation failed. See log file for details.")