# ProcessC <img src="https://github.com/lzwei196/ProcessC/blob/main/logo/logo_processc.jpg" width="100" align="right" />

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.x](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/downloads/)
[![DOI](https://img.shields.io/badge/DOI-10.1016%2Fj.resconrec.2024.108101-blue)](https://doi.org/10.1016/j.resconrec.2024.108101)

**ProcessC** is a comprehensive program designed to monitor energy usage and carbon emissions for running process-based modeling simulations. It provides detailed tracking and analysis of CPU, GPU, and RAM power consumption while calculating total carbon emissions based on country or regional grid carbon intensity.

## 🆕 Latest Updates

ProcessC now offers smart computation grid algorithms based on the computation power of designated CPU/GPU requirements, optimizing energy efficiency for your simulations.

## ✨ Key Features

- **Multi-Component Monitoring**: Tracks CPU, GPU, and RAM energy usage in real-time
- **Carbon Footprint Calculation**: Computes total carbon emissions for running simulations
- **Cross-Platform CPU Support**: Compatible with both Intel and AMD processors
- **Flexible Project Management**: Support for existing projects or new project creation
- **Multiple Data Sources**: Fetches carbon intensity data from various reliable sources
- **Smart Grid Algorithms**: Optimizes computation based on hardware requirements
- **Comprehensive Logging**: Detailed CSV output for analysis and reporting

## 📋 Requirements

- **Python**: 3.x or higher
- **Required Libraries**: 
  ```
  os, json, datetime, pprint, tabulate, requests, pandas, 
  psutil, cpuinfo, GPUtil, logging, csv, art
  ```

## 🚀 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/lzwei196/ProcessC.git
   cd ProcessC
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ensure configuration**:
   Make sure `conf.json` is available in the working directory.

## 📖 Usage

### Prerequisites

Before running ProcessC, ensure you have:

1. **CLI Command**: Your process-based model must be executable from command line (required for bash mode)
2. **Process Name**: The exact name of your program as it appears in system processes
3. **Model Directory**: The working directory path of your model

### Getting Started

Launch ProcessC with:
```bash
python main.py
```

### Configuration Options

ProcessC automatically checks for existing projects in `conf.json`. If none are found, you'll be guided through creating a new project:

1. **Project Setup**:
   - Enter project name
   - Choose monitoring mode (Bash or Direct)
   - Configure mode-specific parameters

2. **System Configuration**:
   - Auto-detection of CPU and GPU specifications
   - Manual input option for custom configurations
   - Grid carbon intensity data source selection

3. **Save Configuration**:
   - Project settings saved for future use
   - Reusable configurations for similar simulations

### Monitoring Process

Once configured, ProcessC will:

- **Real-time Monitoring**: Continuously track energy consumption
- **Data Logging**: Record CPU, GPU, and RAM power usage
- **Emission Calculation**: Compute total energy usage and carbon footprint
- **Results Output**: Generate tabular results and CSV files

## 📊 Example Output

| Metric                            | Value     |
|-----------------------------------|-----------|
| Project Name                      | MyProject |
| Elapsed Time (seconds)            | 3,600     |
| CPU Energy (kWh)                  | 0.05      |
| GPU Energy (kWh)                  | 0.03      |
| RAM Power Usage (kWh)             | 0.02      |
| **Total Energy Usage (kWh)**      | **0.10**  |
| Grid Carbon Intensity (gCO₂/kWh)  | 500.0     |
| **Total Carbon Emission (gCO₂)**  | **50.0**  |

## 🔧 Advanced Features

### Auto-Calibration Support

ProcessC can serve as a wrapper for auto-calibration processes:
- Currently supports **RS-DPCF** auto-calibration
- Extensible architecture for other auto-calibration software
- Contact us for additional software support

### System Capabilities

- **Automatic System Detection**: CPU, GPU, and RAM specifications
- **Connectivity Verification**: Internet connection status checking
- **Location Services**: Automatic region and country detection
- **Comprehensive Logging**: All monitoring data saved to CSV files in `/output` folder

## ⚠️ Important Notes

### Platform-Specific Considerations

- **AMD CPUs on Windows**: Cannot use Intel Power Gadget; uses AMD's default TDP values instead
- **Direct Mode**: ProcessC verifies if the target program is running
- **CMD-Based Executables**: May appear as "OpenConsole.log" - ensure no other programs with this name are running

### Data Source Information

- **OurWorldInData**: Local database (no internet required)
- **ElectricityMap**: Requires paid subscription or manual carbon intensity input for specific locations/years

## 📚 Citation

If you use ProcessC in your research, please cite our paper:

```bibtex
@article{processc2024,
  title={ProcessC: Energy and Carbon Emission Monitoring for Process-Based Modeling Simulations},
  journal={Resources, Conservation and Recycling},
  year={2024},
  doi={10.1016/j.resconrec.2024.108101},
  url={https://doi.org/10.1016/j.resconrec.2024.108101}
}
```

## 👥 Development Team

**Developers**: Ziwei Li, Zhiming Qi, Birk Li, Junzeng Xu, Ruiqi Wu, Yuchen Liu

**Affiliations**: 
- Qi Lab, McGill University, Bioresource Engineering
- Hohai University

## 📞 Support & Contact

For questions, support requests, or additional process-based model integration:

📧 **Email**: [leo.li@mail.mcgill.ca](mailto:leo.li@mail.mcgill.ca)

We welcome feedback and are happy to provide support for integrating additional process-based models.

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**ProcessC** - Making environmental impact monitoring accessible for computational research

[🌟 Star us on GitHub](https://github.com/lzwei196/ProcessC) | [📖 Read the Paper](https://doi.org/10.1016/j.resconrec.2024.108101) | [🐛 Report Issues](https://github.com/lzwei196/ProcessC/issues)

</div>
