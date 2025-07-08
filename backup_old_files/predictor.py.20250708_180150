import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer


class EquipmentReliabilityPredictor:
    def __init__(self, model_path="ml_models/multi_output_model.pkl", data_path="ml_models/Taqathon_data_01072025.xlsx"):
        """
        Initialize the predictor with model and preprocessing components.
        
        Args:
            model_path: Path to the trained model file
            data_path: Path to the training data for fitting encoders and vectorizer
        """
        self.model_path = model_path
        self.data_path = data_path
        self.model = None
        self.label_encoders = {}
        self.vectorizer = None
        # Expected outputs: Fiabilité Intégrité, Disponibilité, Process Safety, Criticité
        self.target_columns = ["Fiabilité Intégrité", "Disponibilité", "Process Safety", "Criticité"]
        
        self._load_model_and_preprocessors()
        self.validate_model()  # Validate model after loading
    
    def _load_model_and_preprocessors(self):
        """Load the model and fit the preprocessors"""
        try:
            print(f"Loading model from: {self.model_path}")
            # Load model
            loaded_obj = joblib.load(self.model_path)
            print(f"Loaded object type: {type(loaded_obj)}")
            
            # Check if loaded object is the actual model or a wrapper
            if hasattr(loaded_obj, 'predict'):
                self.model = loaded_obj
                print("Model loaded successfully - has predict method")
            elif isinstance(loaded_obj, dict) and 'model' in loaded_obj:
                # Use the saved preprocessors from the model file
                self.model = loaded_obj['model']
                self.label_encoders = loaded_obj.get('label_encoders', {})
                self.vectorizer = loaded_obj.get('vectorizer', None)
                print("Model and preprocessors loaded from saved dictionary")
                print(f"Available label encoders: {list(self.label_encoders.keys())}")
                print(f"Vectorizer available: {self.vectorizer is not None}")
                return  # Skip fitting since we have the saved preprocessors
            elif isinstance(loaded_obj, dict):
                # If it's just a dictionary, we need to check what's inside
                print(f"Loaded object is a dictionary with keys: {loaded_obj.keys()}")
                # Try to find a model-like object
                for key, value in loaded_obj.items():
                    if hasattr(value, 'predict'):
                        self.model = value
                        print(f"Found model in dictionary key: {key}")
                        break
                
                if self.model is None:
                    raise ValueError("No model with predict method found in loaded dictionary")
            else:
                raise ValueError(f"Loaded object is not a valid model: {type(loaded_obj)}")
            
            print(f"Final model type: {type(self.model)}")
            
            print(f"Loading data from: {self.data_path}")
            # Load data for fitting encoders and vectorizer
            df = pd.read_excel(self.data_path)
            print(f"Data loaded successfully, shape: {df.shape}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Match the preprocessing from model.py
            df = df.drop(columns=["Date de détéction de l'anomalie", "Section propriétaire"], errors="ignore")
            df = df.fillna("unknown")
            
            # Fit label encoders for the correct features based on model training
            # From model inspection: Num_equipement, Systeme, Description de l'équipement
            input_categorical_cols = ["Num_equipement", "Systeme", "Description de l'équipement"]
            for col in input_categorical_cols:
                if col in df.columns:
                    print(f"Fitting label encoder for input feature: {col}")
                    le = LabelEncoder()
                    df[col] = le.fit_transform(df[col].astype(str))
                    self.label_encoders[col] = le
                    print(f"  Unique values in {col}: {len(le.classes_)}")
                else:
                    print(f"Warning: Input feature column {col} not found in data")
            
            # Fit vectorizer for text description (not the categorical one)
            # Look for a text description column
            text_desc_col = None
            for col in df.columns:
                if 'description' in col.lower() and col != "Description de l'équipement":
                    text_desc_col = col
                    break
            
            if text_desc_col:
                print(f"Fitting vectorizer for text description column: {text_desc_col}")
                self.vectorizer = CountVectorizer(max_features=100, stop_words='english')
                self.vectorizer.fit(df[text_desc_col].astype(str))
                print("Vectorizer fitted successfully")
            else:
                print("Warning: No text description column found for vectorizer")
                
        except Exception as e:
            print(f"Error in _load_model_and_preprocessors: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def _preprocess_input(self, input_dict):
        """
        Preprocess a single input dictionary into feature vector
        
        Expected API input: {"Num_equipement": "...", "Systeme": "...", "Description": "..."}
        Model expects: Num_equipement (encoded), Systeme (encoded), Description de l'équipement (encoded), + vectorized text (100 features)
        
        Args:
            input_dict: Dictionary with keys: "Num_equipement", "Systeme", "Description"
            
        Returns:
            numpy array: Preprocessed feature vector with 103 features
        """
        row = input_dict.copy()
        
        # Extract and encode the categorical features: Num_equipement, Systeme, Description de l'équipement
        categorical_features = []
        
        # Map API Description to model's Description de l'équipement categorical feature
        if "Description" in row:
            row["Description de l'équipement"] = row["Description"]
        
        for col in ["Num_equipement", "Systeme", "Description de l'équipement"]:
            if col in self.label_encoders:
                le = self.label_encoders[col]
                # Get value from input, mapping Description -> Description de l'équipement
                if col == "Description de l'équipement":
                    val = str(row.get("Description", "unknown"))
                else:
                    val = str(row.get(col, "unknown"))
                
                # If unseen label, use 0 as fallback
                if val in le.classes_:
                    encoded_val = le.transform([val])[0]
                else:
                    print(f"Warning: Unseen value '{val}' for {col}, using fallback 0")
                    encoded_val = 0
                categorical_features.append(encoded_val)
            else:
                print(f"Warning: No encoder for {col}, using 0")
                categorical_features.append(0)
        
        # Vectorize the Description field for text features
        desc = str(row.get("Description", "unknown"))
        if self.vectorizer is not None:
            text_features = self.vectorizer.transform([desc]).toarray()
        else:
            # Fallback if vectorizer not available
            text_features = np.zeros((1, 100))
        
        # Compose feature vector: [Num_equipement, Systeme, Description de l'équipement] + Description_vector (100)
        # Total: 3 categorical + 100 text = 103 features
        categorical_features = np.array([categorical_features])
        X = np.concatenate([categorical_features, text_features], axis=1)
        
        print(f"Feature vector shape: {X.shape}")
        print(f"Categorical features count: {len(categorical_features[0])}")
        print(f"Categorical features: {categorical_features}")
        print(f"Text features shape: {text_features.shape}")
        
        if X.shape[1] != 103:
            print(f"Warning: Feature vector has {X.shape[1]} features, expected 103")
        
        return X
    
    def predict_single(self, input_dict):
        """
        Predict for a single equipment reliability assessment
        
        Args:
            input_dict: Dictionary containing equipment data
            
        Returns:
            numpy array: Prediction for the four target variables
        """
        try:
            # Validate model first
            if self.model is None:
                raise ValueError("Model is not loaded")
            
            if not hasattr(self.model, 'predict'):
                raise ValueError(f"Model object does not have predict method. Type: {type(self.model)}")
            
            print(f"Making prediction for input: {input_dict}")
            X = self._preprocess_input(input_dict)
            print(f"Preprocessed input shape: {X.shape}")
            
            prediction = self.model.predict(X)
            print(f"Raw prediction: {prediction}")
            print(f"Prediction shape: {prediction.shape}")
            
            # Extract the three ML predictions: Fiabilité Intégrité, Disponibilité, Process Safety
            raw_prediction = prediction[0]
            
            # Ensure we have at least 3 values
            if len(raw_prediction) < 3:
                raise ValueError(f"Model returned {len(raw_prediction)} values, expected at least 3")
            
            fiabilite_integrite = float(raw_prediction[0])
            disponibilite = float(raw_prediction[1]) 
            process_safety = float(raw_prediction[2])
            
            # Calculate Criticité based on the three ML predictions
            criticite = self.calculate_criticite(fiabilite_integrite, disponibilite, process_safety)
            
            # Return as dictionary with correct output names
            result = {
                "Fiabilité Intégrité": fiabilite_integrite,
                "Disponibilité": disponibilite,
                "Process Safety": process_safety,
                "Criticité": criticite
            }
            
            print(f"Final prediction result: {result}")
            return result
        
        except Exception as e:
            print(f"Error in predict_single: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def predict_batch(self, input_list):
        """
        Predict for a batch of equipment reliability assessments
        
        Args:
            input_list: List of dictionaries containing equipment data
            
        Returns:
            list: List of prediction dictionaries
        """
        if not input_list:
            return []
        
        results = []
        for input_dict in input_list:
            try:
                result = self.predict_single(input_dict)
                results.append(result)
            except Exception as e:
                print(f"Error predicting for {input_dict}: {str(e)}")
                # Return default values on error
                results.append({
                    "Fiabilité Intégrité": 0.5,
                    "Disponibilité": 0.5,
                    "Process Safety": 0.5,
                    "Criticité": "Moyenne"
                })
        
        return results
    
    def predict_from_file(self, file_path, output_path=None):
        """
        Predict equipment reliability from CSV or Excel file
        
        Args:
            file_path: Path to input file (CSV or Excel)
            output_path: Optional path to save results (if None, returns DataFrame)
            
        Returns:
            pandas.DataFrame: DataFrame with original data and predictions
        """
        # Read file based on extension
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            raise ValueError("File must be CSV or Excel format")
        
        # Fill missing values
        df_processed = df.fillna("unknown")
        
        # Convert to list of dictionaries
        input_list = df_processed.to_dict('records')
        
        # Make predictions
        predictions = self.predict_batch(input_list)
        
        # Create results DataFrame
        results_df = df.copy()
        
        # Add prediction columns
        for i, col in enumerate(self.target_columns):
            results_df[f'{col}_predicted'] = predictions[:, i]
        
        # Save to file if output path provided
        if output_path:
            if output_path.endswith('.csv'):
                results_df.to_csv(output_path, index=False)
            elif output_path.endswith(('.xlsx', '.xls')):
                results_df.to_excel(output_path, index=False)
            else:
                raise ValueError("Output file must be CSV or Excel format")
        
        return results_df

    def validate_model(self):
        """Validate that the model is properly loaded and functional"""
        if self.model is None:
            raise ValueError("Model is not loaded")
        
        if not hasattr(self.model, 'predict'):
            raise ValueError(f"Loaded object does not have predict method. Type: {type(self.model)}")
        
        # Test with dummy data
        try:
            dummy_input = np.array([[0, 0, 0] + [0] * 100])  # 3 categorical + 100 text features
            test_pred = self.model.predict(dummy_input)
            print(f"Model validation successful. Output shape: {test_pred.shape}")
            return True
        except Exception as e:
            raise ValueError(f"Model validation failed: {str(e)}")
    
    def calculate_criticite(self, fiabilite_integrite, disponibilite, process_safety):
        """
        Calculate Criticité based on the three ML predicted values
        
        Args:
            fiabilite_integrite: Reliability integrity score
            disponibilite: Availability score  
            process_safety: Process safety score
            
        Returns:
            str: Criticité level (Faible, Moyenne, Élevée, Critique)
        """
        # Simple criticality calculation based on averages and thresholds
        avg_score = (fiabilite_integrite + disponibilite + process_safety) / 3
        
        if avg_score >= 0.8:
            return "Faible"
        elif avg_score >= 0.6:
            return "Moyenne"
        elif avg_score >= 0.4:
            return "Élevée"
        else:
            return "Critique"


# Keep backward compatibility
class AnomalyPredictor(EquipmentReliabilityPredictor):
    """Backward compatibility alias"""
    pass
