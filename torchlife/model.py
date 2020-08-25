# AUTOGENERATED! DO NOT EDIT! File to edit: 90_model.ipynb (unless otherwise specified).

__all__ = ['ModelHazard', 'ModelAFT']

# Cell
import torch
import torch.nn as nn
from .models.ph import PieceWiseHazard
from .models.cox import ProportionalHazard
from .models.aft import AFTModel

from .data import create_db, create_test_dl, get_breakpoints

from .losses import *

from fastai.basics import Learner

# Cell
_text2model_ = {
    'ph': PieceWiseHazard,
    'cox': ProportionalHazard
}

# Cell
class ModelHazard:
    """
    Modelling instantaneous hazard (λ).
    parameters:
    - model(str): ['ph'|'cox'] which maps to Piecewise Hazard, Cox Proportional Hazard.
    - percentiles: list of time percentiles at which time should be broken
    - h: list of hidden units (disregarding input units)
    - bs: batch size
    - epochs: epochs
    - lr: learning rate
    - beta: l2 penalty on weights
    """
    def __init__(self, model:str, percentiles=[20, 40, 60, 80], h:tuple=(),
                 bs:int=128, epochs:int=20, lr:float=1.0, beta:float=0):
        self.model = _text2model_[model]
        self.percentiles = percentiles
        self.loss = hazard_loss
        self.h = h
        self.bs, self.epochs, self.lr, self.beta = bs, epochs, lr, beta
        self.learner = None

    def create_learner(self, df):
        breakpoints = get_breakpoints(df, self.percentiles)
        db, t_scaler, x_scaler = create_db(df, breakpoints)
        dim = df.shape[1] - 2
        assert dim > 0, ValueError("dimensions of x input needs to be >0. Choose ph instead")

        model_args = {
            'breakpoints': breakpoints,
            't_scaler': t_scaler,
            'x_scaler': x_scaler,
            'h': self.h,
            'dim': dim
        }
        self.model = self.model(**model_args)
        self.learner = Learner(db, self.model, loss_func=self.loss, wd=self.beta)

        self.breakpoints = breakpoints
        self.t_scaler = t_scaler
        self.x_scaler = x_scaler

    def lr_find(self, df):
        if self.learner is None:
            self.create_learner(df)

        self.learner.lr_find(wd=self.beta)
        self.learner.recorder.plot()

    def fit(self, df):
        if self.learner is None:
            self.create_learner(df)
        self.learner.fit(self.epochs, lr=self.lr, wd=self.beta)

    def predict(self, df):
        test_dl = create_test_dl(df, self.breakpoints, self.t_scaler, self.x_scaler)
        with torch.no_grad():
            self.model.eval()
            λ, S = [], []
            for x in test_dl:
                preds = self.model(*x)
                λ.append(torch.exp(preds[0]))
                S.append(torch.exp(-preds[1]))
            return torch.cat(λ), torch.cat(S)

    def plot_survival_function(self, *args):
        self.model.plot_survival_function(*args)

# Cell
from .models.error_dist import *

class ModelAFT:
    """
    Modelling error distribution given inputs x.
    parameters:
    - dist(str): Univariate distribution of error
    - h: list of hidden units (disregarding input units)
    - bs: batch size
    - epochs: epochs
    - lr: learning rate
    - beta: l2 penalty on weights
    """
    def __init__(self, dist:str, h:tuple=(),
                 bs:int=128, epochs:int=20, lr:float=1, beta:float=0):
        self.dist = dist
        self.loss = aft_loss
        self.h = h
        self.bs, self.epochs, self.lr, self.beta = bs, epochs, lr, beta
        self.learner = None

    def create_learner(self, df):
        dim = df.shape[1] - 2
        db = create_db(df)
        self.model = AFTModel(self.dist, dim, self.h)
        self.learner = Learner(db, self.model, loss_func=self.loss, wd=self.beta)

    def lr_find(self, df):
        if self.learner is None:
            self.create_learner(df)

        self.learner.lr_find(wd=self.beta)
        self.learner.recorder.plot()

    def fit(self, df):
        if self.learner is None:
            self.create_learner(df)
        self.learner.fit(self.epochs, lr=self.lr, wd=self.beta)

    def predict(self, df):
        test_dl = create_test_dl(df)
        with torch.no_grad():
            self.model.eval()
            Λ = []
            for x in test_dl:
                _, logΛ = self.model(*x)
                Λ.append(torch.log(logΛ))
            return torch.cat(Λ)

    def plot_survival(self, *args):
        self.model.plot_survival_function(*args)