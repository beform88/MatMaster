# MatMaster Agent Project

A multi-agent based platform for materials science computation and data analysis, integrating various computational
tools and database interfaces to provide intelligent solutions for materials research.

## Project Structure

```text
.
├── README.md # Project documentation
├── __init__.py # Python package initialization
├── agents/ # Agent modules directory
│ ├── matmaster_agent/ # Main agent module
│ │ ├── base_agents/ # Base agent classes
│ │ ├── ABACUS_agent/ # ABACUS calculation agent
│ │ ├── DPACalculator_agent/ # DPA calculation agent
│ │ ├── HEACalculator_agent/ # HEA calculation agent
│ │ ├── HEA_assistant_agent/ # HEA assistant agent
│ │ ├── INVAR_agent/ # INVAR materials agent
│ │ ├── MrDice_agent/ # Materials database agent
│ │ ├── chembrain_agent/ # ChemBrain analysis agent
│ │ ├── ssebrain_agent/ # Solid-state electrolyte agent
│ │ └── ... # Other specialized domain agents
│ └── __init__.py
├── evaluate/ # Evaluation module
│ ├── experiments/ # Experimental evaluations
│ ├── metric/ # Evaluation metrics
│ └── base/ # Evaluation base classes
├── pyproject.toml # Python project configuration
└── uv.lock # Dependency lock file
```

## Features

### Computational Tools Integration

- **ABACUS**: First-principles calculations
- **DPA Calculator**: Deep potential calculations
- **HEA Calculator**: High-entropy alloy calculations

### Specialized Domain Agents

- **Chemical Materials Analysis**: Molecular structure, reaction path analysis
- **Solid-State Electrolyte Research**: Ion conductor material screening and analysis
- **Thermoelectric Materials**: Thermoelectric property calculation and optimization
- **Superconducting Materials**: Superconducting characteristic analysis and prediction
- **Perovskite Materials**: Photovoltaic material research and design

### Database Interfaces

- **MrDice**: Materials database query

### Auxiliary Tools

- Structure generation and optimization
- Trajectory analysis
- Document parsing
- Reaction path planning

## Installation & Usage

### Requirements

- Python 3.12+
- google-adk
- uv

### Installation Steps

```bash
# Clone the project
git clone <repository-url>
cd MatMaster/

# Install dependencies
uv sync
```

## Configuration

The project uses `pyproject.toml` for dependency management, including:

- Model API key settings

- Computational resource allocation

- Database connection configuration

- Log level settings

## Evaluation System

The project includes a comprehensive evaluation module supporting:

- Single-turn dialogue evaluation

- Multi-turn dialogue evaluation

- Task transfer quality assessment

- Human simulation evaluation

## Contributing

Welcome to submit Issues and Pull Requests to help improve the project.

## Support

Please submit Issues or contact the development team if you have any questions.
