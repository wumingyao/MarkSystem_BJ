from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb
import lightgbm as lgb
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import ShuffleSplit
from sklearn.metrics import fbeta_score, make_scorer
from sklearn.metrics import r2_score
from sklearn.model_selection import GridSearchCV

def getXGBmodel():
    xgb_regressor = xgb.XGBRegressor(seed=2018, nthread=16)
    cv_sets_xgb = ShuffleSplit(random_state=10)
    parameters_xgb = {'n_estimators': [500, 1000, 2000, 5000], 'learning_rate': [
        0.01, 0.05, 0.07], 'max_depth': [5, 6, 7], 'min_child_weight': [1, 1.5, 2]}
    scorer_xgb = make_scorer(r2_score)
    grid_obj_xgb = GridSearchCV(
        xgb_regressor, parameters_xgb, scoring=scorer_xgb, cv=cv_sets_xgb)
    return grid_obj_xgb
