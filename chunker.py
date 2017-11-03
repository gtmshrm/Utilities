class Chunker:
    def __init__(self, target_file, chunk_size):
        """File chunker which chunks single file into chunks of specified size

        Args:
          target_file: A `str` containing path to target file (.txt)
          chunk_size: An `int` containing size of chunk size in bytes
        """
        self.target_file = target_file
        self.fptr = open(self.target_file, 'rb')
        self.chunk_size = chunk_size
        self.chunk_count = 0

    def chunk_target(self):
        """Chunk and save chunks with target filename postfixed with chunk number

        Example:
        target file => ~/data/output.txt
        chunks => ~/data/output1.txt,~/data/output2.txt,...,~/data/outputN.txt
        """
        chunk = self.fptr.read(self.chunk_size)
        while chunk != b'':
            print('Creating chunk number --> {}'.format(self.chunk_count+1))
            lines = chunk.decode('utf-8', 'ignore').split('\n')
            output_file = self.target_file.replace('.txt', '')+str(self.chunk_count)+'.txt'
            with open(output_file, 'w') as f:
                f.write("\n".join(lines))
            self.chunk_count += 1
            chunk = self.fptr.read(self.chunk_size)


if __name__ == '__main__':
    chunker_client = Chunker(
                        target_file='/home/gtmshrm/Desktop/test2/todo.txt',
                        chunk_size=1024) # 1 KB
    chunker_client.chunk_target()
