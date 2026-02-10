try:
    from execucao.utils import setup_logger
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from execucao.utils import setup_logger

import json
import os
from datetime import datetime, timedelta

logger = setup_logger('PricingEngine')

class PricingEngine:
    def __init__(self):
        self.default_price = 9.0
        self.min_price = 5.0
        self.max_price = 29.0
        self.price_history_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'logs',
            'price_history.jsonl'
        )

    def optimize_price(self, product_id, current_metrics, current_price):
        """
        Decides the new price based on conversion rate.
        """
        visits = current_metrics.get('visits', 0)
        conversion_rate = current_metrics.get('conversion_rate', 0.0)

        # Need minimum data to decide
        if visits < 100:
            logger.info(f"Not enough data for {product_id} (visits={visits}). Keeping price ${current_price}")
            return current_price

        # Simple algorithm
        if conversion_rate < 0.01: # Less than 1%
            new_price = max(self.min_price, current_price * 0.8) # Drop 20%
            logger.info(f"Low conversion ({conversion_rate:.2%}). Dropping price to ${new_price:.2f}")
            return new_price
        
        elif conversion_rate > 0.05: # More than 5%
            new_price = min(self.max_price, current_price * 1.2) # Raise 20%
            logger.info(f"High conversion ({conversion_rate:.2%}). Raising price to ${new_price:.2f}")
            return new_price

        return current_price
    
    def test_price_variants(self, product_id, base_price):
        """
        Create 3 price variants for A/B testing: base, +20%, -20%
        
        Returns:
            dict: {
                'variant_a': base_price,
                'variant_b': base_price * 1.2,
                'variant_c': base_price * 0.8
            }
        """
        variant_b = min(self.max_price, base_price * 1.2)
        variant_c = max(self.min_price, base_price * 0.8)
        
        variants = {
            'variant_a': round(base_price, 2),
            'variant_b': round(variant_b, 2),
            'variant_c': round(variant_c, 2)
        }
        
        logger.info(f"Price variants for {product_id}: A=${variants['variant_a']}, B=${variants['variant_b']}, C=${variants['variant_c']}")
        
        # Log variant creation
        self._log_price_change(product_id, base_price, variants, 'variant_test_created')
        
        return variants
    
    def rollback_price(self, product_id, reason):
        """
        Revert to previous price if conversion drops > 40%
        
        Args:
            product_id: ID of the product
            reason: Reason for rollback
            
        Returns:
            float: Previous price or current if no history
        """
        logger.warning(f"ROLLBACK triggered for {product_id}: {reason}")
        
        # Try to read price history
        try:
            if not os.path.exists(self.price_history_file):
                logger.error("No price history found. Cannot rollback.")
                return self.default_price
            
            # Read last price change before current
            with open(self.price_history_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            product_history = [{
                **json.loads(line),
                'timestamp': line  # Keep raw for ordering
            } for line in lines if json.loads(line).get('product_id') == product_id]
            
            if len(product_history) < 2:
                logger.warning(f"Not enough history for {product_id}. Using default price.")
                return self.default_price
            
            # Get second-to-last price (before current)
            previous_price = product_history[-2].get('new_price', self.default_price)
            
            logger.info(f"Rolling back {product_id} to ${previous_price}")
            self._log_price_change(product_id, previous_price, previous_price, f'rollback: {reason}')
            
            return previous_price
            
        except Exception as e:
            logger.error(f"Error during rollback: {e}")
            return self.default_price
    
    def select_winner_product(self, product_ids, metrics_by_product):
        """
        Compare metrics between product variations and select winner.
        Winner is based on: conversion_rate * avg_revenue
        
        Args:
            product_ids: List of product IDs to compare
            metrics_by_product: Dict mapping product_id -> metrics dict
            
        Returns:
            str: ID of winning product
        """
        if not product_ids or not metrics_by_product:
            logger.warning("No products to compare")
            return None
        
        scores = {}
        
        for pid in product_ids:
            metrics = metrics_by_product.get(pid, {})
            
            visits = metrics.get('visits', 0)
            if visits < 100:
                logger.info(f"Product {pid} has insufficient data (visits={visits})")
                scores[pid] = 0.0
                continue
            
            conversion_rate = metrics.get('conversion_rate', 0.0)
            avg_revenue = metrics.get('avg_revenue', 0.0)
            
            # Score: value per visitor
            score = conversion_rate * avg_revenue
            scores[pid] = score
            
            logger.info(f"Product {pid}: CR={conversion_rate:.2%}, Revenue=${avg_revenue:.2f}, Score={score:.4f}")
        
        if not scores:
            return None
        
        winner_id = max(scores, key=scores.get)
        winner_score = scores[winner_id]
        
        logger.info(f"🏆 WINNER: {winner_id} with score {winner_score:.4f}")
        
        # Log winner selection
        self._log_price_change(
            winner_id,
            None,
            None,
            f'selected_as_winner (score={winner_score:.4f})'
        )
        
        # Pause losers
        for pid in product_ids:
            if pid != winner_id:
                logger.info(f"⏸️ Pausing product {pid} (loser)")
                self._log_price_change(pid, None, None, 'paused_as_loser')
        
        return winner_id
    
    def _log_price_change(self, product_id, old_price, new_price, reason):
        """
        Log price change to price_history.jsonl
        """
        try:
            os.makedirs(os.path.dirname(self.price_history_file), exist_ok=True)
            
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'product_id': product_id,
                'old_price': old_price,
                'new_price': new_price,
                'reason': reason
            }
            
            with open(self.price_history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log price change: {e}")
