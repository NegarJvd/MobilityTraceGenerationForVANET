import arabic_reshaper
from bidi.algorithm import get_display
# import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import numpy as np

class Ns2NodeUtility:
    def __init__(self, file_name):
        self.file_name = file_name
        self.node_times = {}
        self.node_x = {}
        self.node_y = {}
        self._parse_file()

    def _parse_file(self):
        """ Parses the NS-2 mobility trace file and extracts node movement data """
        node_ids = set()
        pattern = re.compile(r"\$ns_ at (\d*\.\d*) \"\$node_\((\d*)\) setdest (\d*\.\d*) (\d*\.\d*)")

        with open(self.file_name, "r") as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    time, node_id, x, y = float(match[1]), int(match[2]), float(match[3]), float(match[4])

                    if node_id in node_ids:
                        entry_time, _ = self.node_times[node_id]
                        self.node_times[node_id] = (entry_time, time)

                        min_x, max_x = self.node_x[node_id]
                        min_y, max_y = self.node_y[node_id]
                        self.node_x[node_id] = (min(min_x, x), max(max_x, x))
                        self.node_y[node_id] = (min(min_y, y), max(max_y, y))
                    else:
                        self.node_times[node_id] = (time, time)
                        self.node_x[node_id] = (x, x)
                        self.node_y[node_id] = (y, y)
                        node_ids.add(node_id)

    def get_n_nodes(self):
        return len(self.node_times)

    def get_entry_time(self, node_id):
        return self.node_times[node_id][0]

    def get_exit_time(self, node_id):
        return self.node_times[node_id][1]

    def get_min_x(self, node_id):
        return self.node_x[node_id][0]

    def get_max_x(self, node_id):
        return self.node_x[node_id][1]

    def get_min_y(self, node_id):
        return self.node_y[node_id][0]

    def get_max_y(self, node_id):
        return self.node_y[node_id][1]

    def get_simulation_time(self):
        return max(exit_time for _, exit_time in self.node_times.values())

    def get_simulation_x_range(self):
        min_x = min(x[0] for x in self.node_x.values())
        max_x = max(x[1] for x in self.node_x.values())
        return (min_x, max_x)

    def get_simulation_y_range(self):
        min_y = min(y[0] for y in self.node_y.values())
        max_y = max(y[1] for y in self.node_y.values())
        return (min_y, max_y)

    def plot_node_activity(self, file_name="plot.png"):
        """ Plot node activity as a timeline (Gantt Chart) """
        fig, ax = plt.subplots(figsize=(12, 6))

        for i, (node_id, (start, stop)) in enumerate(sorted(self.node_times.items())):
            ax.barh(y=node_id, width=stop - start, left=start, height=0.6, label=f"Node {node_id}")

        # ax.set_xlabel("Time (s)")
        # ax.set_ylabel("Node ID")
        # ax.set_title("Node Activity Over Time")
        ax.set_xlabel(get_display(arabic_reshaper.reshape("زمان (sثانیه)")))
        ax.set_ylabel(get_display(arabic_reshaper.reshape("شناسه گره")))
        ax.set_title(get_display(arabic_reshaper.reshape("بازه ی زمان فعالیت برای هر گره")))
        ax.grid(axis="x", linestyle="--", alpha=0.7)
        plt.savefig(os.path.join('.', file_name))
        # plt.show()
        plt.close()
    
    def plot_active_vehicles_over_time(self, file_name="plot.png"):
        """ Plot the number of active vehicles at each second """
        if not self.node_times:
            print(f"Skipping {self.file_name}: No data found.")
            return

        time_range = np.arange(0, int(self.get_simulation_time()) + 1)
        active_vehicles = np.zeros_like(time_range)

        for start, stop in self.node_times.values():
            active_vehicles[(time_range >= start) & (time_range <= stop)] += 1

        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(time_range, active_vehicles, color="blue")

        # ax.set_xlabel("Time (s)")
        # ax.set_ylabel("Active Vehicles Count")
        # ax.set_title(f"Number of Active Vehicles Over Time ({self.get_n_nodes()} Nodes)")
        ax.set_xlabel(get_display(arabic_reshaper.reshape("زمان (ثانیه)")))
        ax.set_ylabel(get_display(arabic_reshaper.reshape("تعداد گره های فعال")))
        ax.set_title(get_display(arabic_reshaper.reshape(f"تعداد گره های فعال در هر ثانیه (مجموع {self.get_n_nodes()} گره)")))
        ax.grid(True, linestyle="--", alpha=0.7)

        plt.savefig(os.path.join('.', file_name))
        # plt.show()
        plt.close()


if __name__ == "__main__":
    tcl_files = [f for f in os.listdir() if f.endswith(".tcl")]

    if not tcl_files:
        print("No .tcl files found in the directory.")
    else:
        for tcl_file in tcl_files:
            print(f"Processing {tcl_file}...")
            ns2_parser = Ns2NodeUtility(tcl_file)
            print(f"Total Nodes: {ns2_parser.get_n_nodes()}, Simulation Time: {ns2_parser.get_simulation_time()}s, X Range: {ns2_parser.get_simulation_x_range()}, Y Range: {ns2_parser.get_simulation_y_range()}")
            ns2_parser.plot_node_activity(tcl_file.replace(".tcl", "_node_activity.png"))
            ns2_parser.plot_active_vehicles_over_time(tcl_file.replace(".tcl", "_network_density.png"))