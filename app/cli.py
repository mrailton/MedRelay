import getpass

import click
import typer
from sqlalchemy.orm import Session

from app.enums import UserRole
from app.repositories.organisation import OrganisationRepository
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

        org_repo = OrganisationRepository(db)
        orgs = org_repo.list_all()
        if not orgs:
            typer.echo("No organisations found. Create one first.", err=True)
            raise typer.Exit(1)

        typer.echo("\nAvailable organisations:")
        for o in orgs:
            typer.echo(f"  {o.id}: {o.code} - {o.name}")
        org_id = typer.prompt("Organisation ID", type=int)

        org = org_repo.get(org_id)
        if not org:
            typer.echo("Invalid organisation ID.", err=True)
            raise typer.Exit(1)

        org_role = typer.prompt(
            f"Role in '{org.code}'",
            type=click.Choice([r.value for r in UserRole], case_sensitive=False),
            default=role,
        ).upper()

        user = repo.create(
            name=name,
            email=email,
            password=hash_password(password),
            role=role,
        )
        org_repo.add_user(user.id, org.id, org_role)
        db.commit()
        typer.echo(f"User '{name}' created successfully with role {org_role} in organisation '{org.code}'.")
    finally:
        db.close()


@app.command("org-create")
def org_create() -> None:
    """Create a new organisation."""
    code = typer.prompt("Code (short identifier)")
    name = typer.prompt("Name")

    db: Session = create_session()
    try:
        repo = OrganisationRepository(db)
        if repo.get_by_code(code):
            typer.echo("An organisation with this code already exists.", err=True)
            raise typer.Exit(1)
        repo.create(code, name)
        db.commit()
        typer.echo(f"Organisation '{name}' ({code}) created successfully.")
    finally:
        db.close()


def main() -> None:
    app()


if __name__ == "__main__":
    main()
