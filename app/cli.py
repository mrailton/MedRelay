import getpass

import click
import typer
from sqlalchemy.orm import Session

from app.enums import UserRole
from app.repositories.session import create_session
from app.repositories.user import UserRepository
from app.security import hash_password

app = typer.Typer(name="medrelay", help="MedRelay management commands")


@app.callback()
def _root() -> None:
    """MedRelay CLI."""


@app.command("user-create")
def user_create() -> None:
    """Create a new user interactively."""
    name = typer.prompt("Name")
    email = typer.prompt("Email")
    role = typer.prompt(
        "Role",
        type=click.Choice([r.value for r in UserRole], case_sensitive=False),
        default=UserRole.CONTROLLER.value,
    ).upper()
    password = getpass.getpass("Password: ")
    confirm = getpass.getpass("Confirm Password: ")
    if password != confirm:
        typer.echo("Passwords do not match.", err=True)
        raise typer.Exit(1)
    if len(password) < 8:
        typer.echo("Password must be at least 8 characters.", err=True)
        raise typer.Exit(1)

    db: Session = create_session()
    try:
        repo = UserRepository(db)
        if repo.get_by_email(email):
            typer.echo("A user with this email already exists.", err=True)
            raise typer.Exit(1)
        repo.create(
            name=name,
            email=email,
            password=hash_password(password),
            role=role,
        )
        db.commit()
        typer.echo(f"User '{name}' created successfully with role {role}.")
    finally:
        db.close()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
