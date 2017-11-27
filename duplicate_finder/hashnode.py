import hashlib
import os

from anytree import Node


def lazyproperty(fn):
    attr_name = '_lazy_' + fn.__name__

    @property
    def _lazyproperty(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, fn(self))
        return getattr(self, attr_name)
    return _lazyproperty


def get_file_content_md5(file_path):
    hash_function = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_function.update(chunk)
    return hash_function.digest()


def get_base_name_md5(path):
    hash_function = hashlib.md5()
    hash_function.update(os.path.basename(path).encode('utf8'))
    return hash_function.digest()


def get_file_size(file_path):
    '''
    Wrapper that catches error for broken symlinks or files that were removed
    during execution.
    '''
    try:
        return os.path.getsize(file_path)
    except FileNotFoundError:
        return 0


def get_file_size_md5(file_path):
    hash_function = hashlib.md5()
    hash_function.update(str(get_file_size(file_path)).encode('utf8'))
    return hash_function.digest()


def compute_file_hash(file_path,
                      hash_file_content,
                      hash_file_name,
                      hash_file_size):
    hash_function = hashlib.md5()
    if hash_file_content:
        hash_function.update(get_file_content_md5(file_path))
    if hash_file_name:
        hash_function.update(get_base_name_md5(file_path))
    if hash_file_size:
        hash_function.update(get_file_size_md5(file_path))
    return hash_function.digest()


class HashNode(Node):
    hash_file_content = False
    hash_file_name = True

    @lazyproperty
    def storage_path(self):
        node_names = [str(node.name) for node in self.path]
        return self.separator.join([''] + node_names)

    @lazyproperty
    def storage_size(self):
        if self.is_file:
            return get_file_size(self.storage_path)
        return sum([child.storage_size for child in self.children])
    hash_file_size = True

    @lazyproperty
    def is_file(self):
        return os.path.isfile(self.storage_path)

    @lazyproperty
    def is_link(self):
        return os.path.islink(self.storage_path)

    @lazyproperty
    def hash_md5(self):
        '''
        Recursive lazy property to compute the md5 hash based on the hash of
        all children.
        '''
        if self.is_leaf:
            if self.is_file:
                 return compute_file_hash(self.storage_path,
                                          self.hash_file_content,
                                          self.hash_file_name,
                                          self.hash_file_size)
            elif self.is_link:
                 return get_base_name_md5(self.storage_path)
            else:
                 # Empty directory we only hash its name
                 assert len(os.listdir(self.storage_path)) == 0, \
                        'Non empty directory is a leaf: {}'.format(self.storage_path)
                 return get_base_name_md5(self.storage_path)
        hash_function = hashlib.md5()
        for child in sorted(self.children, key=lambda c: c.hash_md5):
            hash_function.update(child.hash_md5)
        return hash_function.digest()

    def is_in_dir(self, dir_path):
        return self.storage_path.startswith(dir_path)
