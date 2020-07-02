# AUTOGENERATED! DO NOT EDIT! File to edit: 20_KaplanMeier.ipynb (unless otherwise specified).

__all__ = ['KaplanMeier']

# Cell
import pandas as pd
import matplotlib.pyplot as plt

# Cell
class KaplanMeier:
    def fit(self, df):
        """
        Estimages the Kaplan-Meier survival function
        parameters:
        - t: time steps
        - e: whether death occured at time step (1) or not (0)
        """
        d = df.groupby("t")["e"].sum()
        n = df.groupby("t")["e"].count()
        n = n[::-1].cumsum()[::-1]
        self.survival_function = (1 - d / n).cumprod()

        if 0 not in self.survival_function:
            self.survival_function[0] = 1
            self.survival_function.sort_index(inplace=True)

    def plot_survival_function(self):
        fig, ax = plt.subplots()
        ax.plot(self.survival_function)
        ax.set_xlabel("Duration")
        ax.set_ylabel("Survival Probability")

        ax.set_title("Survival Function")
        return ax