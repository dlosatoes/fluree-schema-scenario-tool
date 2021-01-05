async def checkpart_main(part, flureedir):
    """Main function for the freezepart subcommand"""
    try:
        partdir = PartDir(flureedir, part)
    except RuntimeError as exp:
        print(exp)
        sys.exit(1)
    print("OK")
