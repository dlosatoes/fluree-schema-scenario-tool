async def refreezedeps_main(part, flureedir):
    """Main function for the refreezedeps subcommand"""
    try:
        partdir = PartDir(flureedir, part)
    except RuntimeError as exp:
        print(exp)
        sys.exit(1)
    partdir.refreeze_deps()
