# AUTOGENERATED! DO NOT EDIT! File to edit: 65_AFT_error_distributions.ipynb (unless otherwise specified).

__all__ = ['gumbel_logpdf', 'gumbel_logcdf', 'gaussian_logpdf', 'gaussian_logcdf', 'get_distribution']

# Cell
import torch
import torch.nn as nn
import torch.nn.functional as F

# Cell
def gumbel_logpdf(z:torch.Tensor):
#     z = t - μ
    return - (z + torch.exp(-z))

def gumbel_logcdf(z:torch.Tensor):
#     z = t - μ
    cdf = 1 - torch.exp(-torch.exp(-z))
    return torch.log(cdf)

# Cell
_gauss = torch.distributions.Normal(0, 1)
def gaussian_logpdf(z:torch.Tensor):
    return _gauss.log_prob(z)

def gaussian_logcdf(z:torch.Tensor):
    cdf = 1 - _gauss.cdf(z)
    return torch.log(cdf)

# Cell
def get_distribution(dist:str, dist_args:tuple=(0,1)):
    """
    Get the logpdf and logcdf of a given torch distribution
    """
    dist = getattr(torch.distributions, dist.title())(*dist_args)
    if not isinstance(dist.support, torch.distributions.constraints._Real):
        raise Exception("Distribution needs support over ALL real values.")

    def dist_logpdf(ξ):
        return dist.log_prob(ξ)

    def dist_logcdf(ξ):
        return torch.log(1 - dist.cdf(ξ))

    return dist_logpdf, dist_logcdf