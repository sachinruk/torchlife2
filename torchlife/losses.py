# AUTOGENERATED! DO NOT EDIT! File to edit: 95_Losses.ipynb (unless otherwise specified).

__all__ = ['aft_loss', 'hazard_loss']

# Cell
def _aft_loss(log_pdf, log_cdf, e):
    lik = e * log_pdf + (1 - e) * log_cdf
    return -lik.mean()

def aft_loss(params, e):
    log_pdf, log_cdf = params
    return _aft_loss(log_pdf, log_cdf, e)

# Cell
def _hazard_loss(logλ, Λ, e):
    log_lik = e * logλ - Λ
    return -log_lik.mean()

def hazard_loss(params, e):
    logλ, Λ = params
    return _hazard_loss(logλ, Λ, e)