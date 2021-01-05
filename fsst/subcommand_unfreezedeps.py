async def unfreezedeps_main(part, flureedir):
    """Main function for the unfreezedeps subcommand"""
    try:
        partdir = PartDir(flureedir, part)
    except RuntimeError as exp:
        print(exp)
        sys.exit(1)
    editfile = partdir.unfreeze_deps()
    print(editfile)
