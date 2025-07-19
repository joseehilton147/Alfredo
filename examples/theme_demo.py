#!/usr/bin/env python3
"""
Demonstration of the CLI theme system.
This script shows how to use the theme system components.
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.presentation.cli.themes import (
    ColorPalette,
    DefaultTheme,
    ThemeManager,
    ThemePresets,
)


def main():
    """Demonstrate the theme system functionality."""
    console = Console()

    # Create theme manager with default theme
    theme_manager = ThemeManager()

    console.print("\n🎨 [bold blue]Alfredo AI - CLI Theme System Demo[/bold blue]\n")

    # Show color palette
    console.print("📋 [bold]Color Palette:[/bold]")
    color_panel = Panel(
        f"[{ColorPalette.CLAUDE_BLUE}]● Claude Blue[/] - Primary actions\n"
        f"[{ColorPalette.CLAUDE_GREEN}]● Claude Green[/] - Success states\n"
        f"[{ColorPalette.CLAUDE_ORANGE}]● Claude Orange[/] - Warnings\n"
        f"[{ColorPalette.CLAUDE_RED}]● Claude Red[/] - Errors\n"
        f"[{ColorPalette.CLAUDE_PURPLE}]● Claude Purple[/] - Accents",
        title="Colors",
        border_style="rounded"
    )
    console.print(color_panel)

    # Demonstrate menu styles
    console.print("\n🍽️ [bold]Menu Styles:[/bold]")
    menu_table = Table(show_header=False, padding=(0, 2))
    menu_table.add_column("Icon", width=3)
    menu_table.add_column("Option")
    menu_table.add_column("Status")

    menu_table.add_row("📁", "Process Local Video", "[green]Available[/green]")
    menu_table.add_row("🎬", "Process YouTube Video", "[green]Available[/green]")
    menu_table.add_row("📦", "Batch Processing", "[green]Available[/green]")
    menu_table.add_row("⚙️", "Settings", "[yellow]Selected[/yellow]")
    menu_table.add_row("📊", "View Results", "[dim]Disabled[/dim]")

    menu_panel = Panel(menu_table, title="Main Menu", border_style="rounded")
    console.print(menu_panel)

    # Demonstrate status messages
    console.print("\n📢 [bold]Status Messages:[/bold]")
    theme_manager.print_success("Video transcription completed successfully!")
    theme_manager.print_error("Failed to download video from URL")
    theme_manager.print_warning("Large file detected - processing may take longer")
    theme_manager.print_info("Starting batch processing of 5 videos")

    # Demonstrate progress bar
    console.print("\n⏳ [bold]Progress Display:[/bold]")
    import time
    with theme_manager.create_progress_bar("Processing video") as progress:
        task = progress.add_task("Transcribing audio...", total=100)
        for i in range(0, 101, 10):
            progress.update(task, completed=i)
            time.sleep(0.1)

    # Show different theme presets
    console.print("\n🎭 [bold]Theme Presets:[/bold]")

    themes = {
        "Default": ThemePresets.get_default_theme(),
        "High Contrast": ThemePresets.get_high_contrast_theme(),
        "Minimal": ThemePresets.get_minimal_theme()
    }

    for name, theme in themes.items():
        scheme = theme.get_color_scheme()
        theme_info = f"Primary: {scheme['primary']} | Success: {scheme['success']} | Error: {scheme['error']}"
        console.print(f"  • [bold]{name}[/bold]: {theme_info}")

    console.print("\n✨ [bold green]Theme system demonstration complete![/bold green]\n")


if __name__ == "__main__":
    main()
