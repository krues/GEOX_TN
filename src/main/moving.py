import os
import shutil

def move_to_target(src, target):
    """
    Move a file or directory `src` into the target directory.
    The destination is target/basename(src).
    """
    if not os.path.exists(src):
        print(f"Warning: source {src} does not exist.")
        return
    dest = os.path.join(target, os.path.basename(src))
    print(f"Moving {src} to {dest}")
    shutil.move(src, dest)

def main():
    # Get the target directory from snakemake.params.
    target = snakemake.params.target
    # Ensure the target directory exists.
    os.makedirs(target, exist_ok=True)
    
    # Process input items.
    # snakemake.input contains: 'results', 'plots', 'resources', and 'xcsv'.
    
    # Handle 'results' input, which is a list of files.
    results = snakemake.input.results
    if isinstance(results, list):
        for src in results:
            move_to_target(src, target)
    else:
        move_to_target(results, target)
    
    # Handle 'plots' input (a directory).
    move_to_target(snakemake.input.plots, target)
    
    # Handle 'resources' input, which is a list of files.
    resources = snakemake.input.resources
    if isinstance(resources, list):
        for src in resources:
            move_to_target(src, target)
    else:
        move_to_target(resources, target)
    
    move_to_target(snakemake.input.lcresults, target)
    # Handle 'xcsv' input (a CSV file).
    move_to_target(snakemake.input.xcsv, target)

if __name__ == "__main__":
    main()
