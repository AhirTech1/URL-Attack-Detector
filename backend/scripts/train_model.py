"""
Train ML model for URL attack detection
Uses Random Forest classifier
"""
import sys
import pandas as pd
import numpy as np
import pickle
import logging
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from detection.feature_extractor import FeatureExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainer:
    """Train and evaluate ML model"""
    
    def __init__(self, data_dir: Path = None, model_dir: Path = None):
        """Initialize trainer"""
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / 'data'
        if model_dir is None:
            model_dir = Path(__file__).parent.parent / 'models'
        
        self.data_dir = Path(data_dir)
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(exist_ok=True)
        
        self.feature_extractor = FeatureExtractor()
        self.model = None
        self.label_encoder = None
    
    def load_dataset(self, filepath: Path) -> pd.DataFrame:
        """Load dataset from CSV"""
        logger.info(f"Loading dataset from {filepath}")
        
        if filepath.suffix == '.csv':
            df = pd.read_csv(filepath)
        elif filepath.suffix == '.json':
            df = pd.read_json(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")
        
        logger.info(f"Loaded {len(df)} samples")
        return df
    
    def extract_features(self, df: pd.DataFrame) -> tuple:
        """Extract features from dataset"""
        logger.info("Extracting features...")
        
        X = []
        y = []
        
        for idx, row in df.iterrows():
            if idx % 1000 == 0:
                logger.info(f"Processed {idx}/{len(df)} samples")
            
            try:
                features = self.feature_extractor.extract(
                    url=row['url'],
                    method=row.get('method', 'GET'),
                    headers={},
                    body=''
                )
                X.append(list(features.values()))
                y.append(row['label'])
            except Exception as e:
                logger.warning(f"Error extracting features for row {idx}: {e}")
                continue
        
        feature_names = list(self.feature_extractor.extract('http://example.com').keys())
        
        logger.info(f"Extracted {len(X)} feature vectors with {len(feature_names)} features each")
        
        return np.array(X), np.array(y), feature_names
    
    def train(self, X_train, y_train):
        """Train Random Forest model"""
        logger.info("Training Random Forest classifier...")
        
        # Encode labels
        self.label_encoder = LabelEncoder()
        y_train_encoded = self.label_encoder.fit_transform(y_train)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'  # Handle imbalanced classes
        )
        
        self.model.fit(X_train, y_train_encoded)
        
        logger.info("Training completed")
    
    def evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        logger.info("Evaluating model...")
        
        y_test_encoded = self.label_encoder.transform(y_test)
        y_pred = self.model.predict(X_test)
        
        # Accuracy
        accuracy = accuracy_score(y_test_encoded, y_pred)
        logger.info(f"Accuracy: {accuracy:.4f}")
        
        # Classification report
        logger.info("\nClassification Report:")
        report = classification_report(
            y_test_encoded, 
            y_pred,
            target_names=self.label_encoder.classes_
        )
        print(report)
        
        # Confusion matrix
        logger.info("\nConfusion Matrix:")
        cm = confusion_matrix(y_test_encoded, y_pred)
        print(cm)
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_names = self.feature_extractor.get_feature_names()
            importances = self.model.feature_importances_
            indices = np.argsort(importances)[::-1][:20]
            
            logger.info("\nTop 20 Most Important Features:")
            for i, idx in enumerate(indices, 1):
                logger.info(f"{i}. {feature_names[idx]}: {importances[idx]:.4f}")
        
        return accuracy
    
    def cross_validate(self, X, y, cv=5):
        """Perform cross-validation"""
        logger.info(f"Performing {cv}-fold cross-validation...")
        
        y_encoded = self.label_encoder.transform(y)
        scores = cross_val_score(self.model, X, y_encoded, cv=cv, scoring='accuracy')
        
        logger.info(f"Cross-validation scores: {scores}")
        logger.info(f"Mean accuracy: {scores.mean():.4f} (+/- {scores.std() * 2:.4f})")
        
        return scores
    
    def save_model(self, filename: str = 'rf_classifier.pkl'):
        """Save trained model"""
        filepath = self.model_dir / filename
        
        model_data = {
            'model': self.model,
            'label_encoder': self.label_encoder,
            'feature_names': self.feature_extractor.get_feature_names()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        
        logger.info(f"Model saved to {filepath}")
        return filepath

def main():
    """Main training pipeline"""
    trainer = ModelTrainer()
    
    # Load training dataset
    train_file = trainer.data_dir / 'train_dataset.csv'
    if not train_file.exists():
        logger.error(f"Training dataset not found at {train_file}")
        logger.info("Please run generate_dataset.py first")
        return
    
    df_train = trainer.load_dataset(train_file)
    
    # Extract features
    X, y, feature_names = trainer.extract_features(df_train)
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Validation set: {len(X_val)} samples")
    
    # Train model
    trainer.train(X_train, y_train)
    
    # Evaluate on validation set
    accuracy = trainer.evaluate(X_val, y_val)
    
    # Cross-validation
    trainer.cross_validate(X_train, y_train, cv=5)
    
    # Save model
    trainer.save_model()
    
    # Test on separate test set if available
    test_file = trainer.data_dir / 'test_dataset.csv'
    if test_file.exists():
        logger.info("\n" + "="*50)
        logger.info("Testing on separate test set")
        logger.info("="*50)
        
        df_test = trainer.load_dataset(test_file)
        X_test, y_test, _ = trainer.extract_features(df_test)
        
        logger.info(f"Test set: {len(X_test)} samples")
        trainer.evaluate(X_test, y_test)

if __name__ == '__main__':
    main()
