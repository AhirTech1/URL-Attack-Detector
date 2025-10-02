"""
Data export utilities
"""
import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class DataExporter:
    """Export detection results to various formats"""
    
    def to_csv(self, results: List[Dict[str, Any]], output_path: Path) -> Path:
        """
        Export results to CSV
        
        Args:
            results: List of detection results
            output_path: Output file path
        
        Returns:
            Path to created file
        """
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                if not results:
                    logger.warning("No results to export")
                    return output_path
                
                # Flatten nested features if present
                flattened_results = []
                for result in results:
                    flat_result = result.copy()
                    if 'features' in flat_result:
                        features = flat_result.pop('features')
                        for key, value in features.items():
                            flat_result[f'feature_{key}'] = value
                    flattened_results.append(flat_result)
                
                fieldnames = flattened_results[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(flattened_results)
            
            logger.info(f"Exported {len(results)} results to CSV: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            raise
    
    def to_json(self, results: List[Dict[str, Any]], output_path: Path) -> Path:
        """
        Export results to JSON
        
        Args:
            results: List of detection results
            output_path: Output file path
        
        Returns:
            Path to created file
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'total_count': len(results),
                    'results': results
                }, f, indent=2)
            
            logger.info(f"Exported {len(results)} results to JSON: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            raise
