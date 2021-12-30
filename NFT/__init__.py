class NFT:

    def __init__(self, name, desc, unlockable_content, ext_url, metadata, file):
        self.name = name
        self.description = desc
        self.metadata = metadata
        self.file = file
        self.external_url = ext_url
        self.unlockable_content = unlockable_content
