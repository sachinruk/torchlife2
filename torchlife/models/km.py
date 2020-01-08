# AUTOGENERATED! DO NOT EDIT! File to edit: KaplanMeier.ipynb (unless otherwise specified).

__all__ = ['PieceWiseHazard', 'km_loss']

# Cell
import torch
import torch.nn as nn
import matplotlib.pyplot as plt
import numpy as np

torch.Tensor.ndim = property(lambda x: x.dim())

# Cell
class PieceWiseHazard(nn.Module):
    """
    Piecewise Hazard where the hazard is constant between breakpoints.
    parameters:
    - breakpoints: time points where hazard would change
    - max_t: maximum point of time to plot to.
    """
    def __init__(self, breakpoints, max_t):
        super().__init__()
        self.logλ = nn.Embedding(len(breakpoints)+1, 1)
        self.breakpoints = torch.Tensor([0] + breakpoints.tolist())
        bounded_bp = [0] + breakpoints.tolist() + [max_t]
        self.widths = torch.Tensor(np.diff(bounded_bp).tolist())[:,None]
        self.zero = torch.zeros(1,1)
        self.max_t = max_t

    def cumulative_hazard(self, t, t_section):
        """
        Integral of hazard wrt time.
        """
        λ = torch.exp(self.logλ.weight)

        # cumulative hazard
        cum_hazard = λ * self.widths
        cum_hazard = cum_hazard.cumsum(0)
        cum_hazard = torch.cat([self.zero, cum_hazard])
        cum_hazard_sec = cum_hazard[t_section]

        δ_t = t - self.breakpoints[t_section][:,None]

        return cum_hazard_sec + λ[t_section] * δ_t

    def forward(self, x, t, t_section):
        return self.logλ(t_section), self.cumulative_hazard(t, t_section)

    def plot_survival_function(self):
        # get the times and time sections for survival function
        t_query = np.arange(self.max_t+10)
        breakpoints = self.breakpoints[1:].cpu().numpy()
        t_sec_query = np.searchsorted(breakpoints, t_query)
        # convert to pytorch tensors
        t_query = torch.Tensor(t_query)[:,None]
        t_sec_query = torch.LongTensor(t_sec_query)

        # calculate cumulative hazard according to above
        cum_haz = self.cumulative_hazard(t_query, t_sec_query)
        surv_fun = torch.exp(-cum_haz)

        # plot
        plt.figure(figsize=(12,5))
        plt.plot(t_query, surv_fun)
        plt.show()

    def plot_hazard(self):
        width = self.widths.cpu().numpy().squeeze()
        x = self.breakpoints.cpu().numpy().squeeze()
        λ = torch.exp(self.logλ.weight)
        y = λ.squeeze()
        # plot
        plt.figure(figsize=(12,5))
        plt.bar(x, y, width, align='edge')
        plt.show()

# Cell
def km_loss(params, e):
    logλ, Λ = params # unpack the estimates parameters
    log_lik = e * logλ - Λ
    return -log_lik.mean()