import mplfinance as mpf
import os


class ChartGenerator:
    def __init__(self, output_dir=None):
        if output_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(base_dir, "output")
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def generate_chart(self, df, filename="chart.png", title="Stock Chart"):
        if df.empty:
            print(f"Warning: Dataframe is empty for {filename}")
            return None

        filepath = os.path.join(self.output_dir, filename)
        filepath = os.path.abspath(filepath)

        s = mpf.make_mpf_style(base_mpf_style="charles", rc={"font.size": 10})

        mpf.plot(
            df,
            type="candle",
            volume=True,
            title=title,
            style=s,
            savefig=dict(fname=filepath, dpi=100, bbox_inches="tight"),
        )
        return filepath
