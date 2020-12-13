import getpass
import os

from .config import gc


def file_exists_check_helper(selectedtext):
    prefix = gc("inline_prefix")
    if not prefix:
        return
    sel = selectedtext.strip().lstrip(prefix)

    sep = gc("inline_separator")
    if sep and sep in sel:
        file, page = sel.split(sep) 
    else:
        file = sel
        page = ""
    root, ext = os.path.splitext(file)
    ext_wo_leading_dot_and_lower = ext[1:].lower()
    all_relative_paths, all_relative_files = get_all_relative()
    outfile, _ = check_if_file_exists(file=file, 
                                   root=root,
                                   ext=ext_wo_leading_dot_and_lower,
                                   rel_folders=all_relative_paths
                                  )
    if not outfile:
        outfile = guess_extension(file, all_relative_files)
    return outfile, page


def guess_extension(sel_file, all_relative_files):
    def compare(sel_file, case_insensitive=False):
        for f in all_relative_files:
            _, base = os.path.split(f)
            filename, _ = os.path.splitext(base)
            if case_insensitive:
                sel_file = sel_file.lower()
                filename = filename.lower()
            if sel_file == filename:
                return f
    out = compare(sel_file)
    if out:
        return out
    out = compare(sel_file, case_insensitive=True)
    if out:
        return out


def check_if_file_exists(file, root, ext, rel_folders):
    if os.path.isabs(file):
        # file also might contain stuff after the extension like "#id-to-open" for html-files
        path_to_check = root + os.extsep + ext
        if os.path.exists(path_to_check):
            return file, ""
        else:
            failmsg = "file '%s' doesn't exist. maybe adjust the config or field values" % file
            return None, failmsg
    else:
        username = getpass.getuser()
        if isinstance(rel_folders, str):
            rel_folders = [rel_folders, ]
        for rp in rel_folders:
            base = rp.replace("MY_USER", username)
            if not base:
                continue
            # file also might contain stuff after the extension like "#id-to-open" for html-files
            path_to_check = base + "/" + root + os.extsep + ext
            if os.path.exists(path_to_check):
                # os.path.join(base, file) - this leads to a mix of "/" and "\" on Windows which fails
                file = base + "/" + file
                return file, ""
        else:
            # file dosn't exist in any of the default paths:
            failmsg = (f"file '{file}' is not in any of the the folders for relative "
                        "paths you've set for the extension "
                       f"{ext}. Maybe adjust the config or "
                        "field value."
                )
            return None, failmsg


def get_all_relative():
    this_config = gc("programs_for_extensions")
    if not this_config:
        return []

    all_relative_paths = []
    all_relative_files = []
    for v in this_config:
        rel = v["default_folder_for_relative_paths"]
        if isinstance(rel, str):
            rel = [rel, ]
        if isinstance(rel, list):
            for e in rel:
                if os.path.isdir(e) and e not in all_relative_paths:
                    all_relative_paths.append(e)
    
    for fp in all_relative_paths:
        for root, _, files in os.walk(fp):
            for name in files:
                all_relative_files.append(os.path.join(root, name))

    return all_relative_paths, all_relative_files
