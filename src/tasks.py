# Copyright (c) 2025- Charudatta
# 
# This software is released under the MIT License.
# https://opensource.org/licenses/MIT


from invoke import task
from pathlib import Path
import os

@task
def build_book(ctx, src_dir='src', output_dir='build', output_file='book', format='pdf', cover_page='cover.md', preface='preface.md'):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/{output_file}.{format}"

    # Collect all markdown files in the source directory
    markdown_files = sorted(Path(src_dir).glob('*.md'))
    markdown_paths = [str(f) for f in markdown_files]

    # Construct the Pandoc command
    pandoc_command = ['pandoc', '-s', '--toc', '--toc-depth=2']

    # Add cover page and preface if they exist
    if Path(cover_page).exists():
        pandoc_command.append(cover_page)
    if Path(preface).exists():
        pandoc_command.append(preface)

    # Add the markdown files
    pandoc_command.extend(markdown_paths)

    # Add format-specific options
    if format == 'pdf':
        pandoc_command.extend(['--template=template.tex', '-o', output_path])
    elif format == 'html':
        pandoc_command.extend(['-c', 'style.css', '-o', output_path])
    else:
        pandoc_command.extend(['-o', output_path])

    # Run the Pandoc command
    try:
        ctx.run(' '.join(pandoc_command))
        print(f"Book successfully built at {output_path}")
    except Exception as e:
        print(f"Error building book: {e}")

@task
def clean(ctx, output_dir='build'):
    # Remove the build directory
    if Path(output_dir).exists():
        ctx.run(f'rm -rf {output_dir}')
        print(f"Cleaned up {output_dir}")
    else:
        print(f"{output_dir} does not exist")
