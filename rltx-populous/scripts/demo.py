#!/usr/bin/env python3
"""
CLI demo script to run simulation and show results.
"""

import asyncio
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box

from backend.data.presets.b2b_saas import get_saas_launch_scenario, get_demo_strategies
from backend.engine import SimulationRunner

console = Console()


def show_header():
    """Display demo header"""
    console.print()
    console.print(Panel.fit(
        "[bold blue]RLTX POPULOUS[/bold blue]\n"
        "[dim]Decision Intelligence Simulation Platform[/dim]",
        border_style="blue"
    ))
    console.print()


def show_scenario(scenario):
    """Display scenario information"""
    segments_text = "\n".join([
        f"  • {s.name}: {s.size_pct*100:.0f}% of market"
        for s in scenario.segments
    ])

    competitors_text = "\n".join([
        f"  • {c.name} ({c.market_share*100:.0f}% share)"
        for c in scenario.competitors
    ])

    console.print(Panel(
        f"[bold]{scenario.name}[/bold]\n"
        f"[dim]{scenario.description}[/dim]\n\n"
        f"[cyan]Market Size:[/cyan] {scenario.total_addressable_market:,} potential buyers\n\n"
        f"[cyan]Segments:[/cyan]\n{segments_text}\n\n"
        f"[cyan]Competitors:[/cyan]\n{competitors_text}\n\n"
        f"[cyan]Your Product:[/cyan] {scenario.your_product.name}",
        title="Scenario",
        border_style="green"
    ))


def show_strategies(strategies):
    """Display strategies to compare"""
    console.print("\n[bold]Strategies to Compare:[/bold]\n")

    for i, strategy in enumerate(strategies, 1):
        console.print(
            f"  {i}. [cyan]{strategy.name}[/cyan] - {strategy.description}"
        )
        console.print(f"     GTM Intensity: {strategy.gtm.intensity*100:.0f}%")
        console.print(f"     Target: {', '.join(strategy.gtm.target_segments)}")
        console.print()


def show_results(results_list):
    """Display comparison results"""
    console.print("\n[bold]SIMULATION RESULTS[/bold]\n")

    # Create results table
    table = Table(show_header=True, header_style="bold magenta", box=box.ROUNDED)
    table.add_column("Strategy")
    table.add_column("Mean Conversion", justify="right")
    table.add_column("90% CI", justify="right")
    table.add_column("Best Case (P95)", justify="right")
    table.add_column("Worst Case (P5)", justify="right")

    for strategy, result in results_list:
        table.add_row(
            strategy.name,
            f"[bold]{result.mean_conversion*100:.1f}%[/bold]",
            f"{result.p5*100:.1f}% - {result.p95*100:.1f}%",
            f"[green]{result.p95*100:.1f}%[/green]",
            f"[red]{result.p5*100:.1f}%[/red]"
        )

    console.print(table)

    # Find winner
    winner_strategy, winner_result = max(results_list, key=lambda x: x[1].mean_conversion)

    console.print(f"\n[bold green]>>> Winner: {winner_strategy.name}[/bold green]")
    console.print(f"    Expected conversion: {winner_result.mean_conversion*100:.1f}%")

    # Segment breakdown for winner
    console.print("\n[bold]Segment Performance (Winner):[/bold]")
    for seg_analysis in winner_result.segment_analysis:
        bar_len = int(seg_analysis.conversion_rate * 50)
        bar = "█" * bar_len + "░" * (50 - bar_len)
        console.print(
            f"  {seg_analysis.segment_name:12} [{bar}] "
            f"[cyan]{seg_analysis.conversion_rate*100:.1f}%[/cyan]"
        )

    # Drivers
    if winner_result.top_drivers:
        console.print("\n[bold]Key Drivers:[/bold]")
        for driver in winner_result.top_drivers[:3]:
            console.print(f"  [green]✓[/green] {driver.factor}")
            console.print(f"    [dim]{driver.description}[/dim]")

    if winner_result.top_blockers:
        console.print("\n[bold]Key Risks:[/bold]")
        for blocker in winner_result.top_blockers[:3]:
            console.print(f"  [red]✗[/red] {blocker.factor}")
            console.print(f"    [dim]{blocker.description}[/dim]")


async def run_demo():
    """Run the demo simulation"""

    show_header()

    # Load scenario
    scenario = get_saas_launch_scenario()
    strategies = get_demo_strategies()

    show_scenario(scenario)
    show_strategies(strategies)

    console.print("[dim]Press Enter to start simulation...[/dim]")
    input()

    # Run simulations
    results_list = []

    for strategy in strategies:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"Simulating [cyan]{strategy.name}[/cyan]...",
                total=None
            )

            runner = SimulationRunner(
                scenario=scenario,
                strategy=strategy,
                num_agents=5000,  # Reduced for demo speed
                num_branches=200,
                use_llm_personas=False,
                parallel=True
            )

            result = runner.run()
            results_list.append((strategy, result))

    show_results(results_list)

    console.print("\n" + "═" * 60)
    console.print(
        "\n[bold]This is what decisions look like when you can see all the futures.[/bold]\n"
    )
    console.print(
        "[dim]What decision are you making this quarter that you wish you could test first?[/dim]\n"
    )


def main():
    """Main entry point"""
    try:
        asyncio.run(run_demo())
    except KeyboardInterrupt:
        console.print("\n[dim]Demo interrupted.[/dim]")
        sys.exit(0)


if __name__ == "__main__":
    main()
