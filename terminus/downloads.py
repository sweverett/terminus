'''
This file contains utility functions for downloading files & extracting archives from remote sources
'''

from pathlib import Path
import requests

# def download_file(url: str, output_dir: Path, vb: bool = False) -> Path:
#     '''
#     Downloads a file from a given URL and saves it to the specified output 
#     directory
    
#     Parameters
#     ----------
#     url : str
#         The URL of the file to download.
#     output_dir : Path
#         The directory where the file should be saved.
#     vb: bool
#         Whether to print verbose output to the terminal

#     Returns
#     -------
#     Path
#         The local path of the downloaded file.
#     '''

#     local_filename = output_dir / Path(url).name

#     print(f'Downloading to {local_filename}...')
    
#     if local_filename.exists():
#         print(f'File already exists and will be skipped: {local_filename}')
#         return local_filename

#     with requests.get(url, stream=True) as r:
#         r.raise_for_status()
#         with local_filename.open('wb') as f:
#             for chunk in r.iter_content(chunk_size=8192):
#                 f.write(chunk)

#     return local_filename

def download_file(url: str, output_dir: Path, vb: bool = True) -> Path:
    '''
    Downloads a file from a given URL and saves it to the specified output 
    directory, with an optional verbose flag to show download progress.
    
    Parameters
    ----------
    url : str
        The URL of the file to download.
    output_dir : str, Path
        The directory where the file should be saved.
    vb: bool
        Whether to print download status updates to the terminal.

    Returns
    -------
    Path
        The local path of the downloaded file.
    '''

    output_dir = Path(output_dir)
    local_filename = output_dir / Path(url).name

    if output_dir.is_dir() is False:
        output_dir.mkdir(parents=True)

    print(f'Downloading to {local_filename}...')

    if local_filename.exists():
        print(f'File already exists and will be skipped: {local_filename}')
        return local_filename

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        downloaded_size = 0
        chunk_size = 8192

        with local_filename.open('wb') as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
                downloaded_size += len(chunk)
                if vb and total_size > 0:
                    percent_complete = (downloaded_size / total_size) * 100
                    print(
                        f'Downloaded {downloaded_size / 1024:,.2f} KB of '
                        f'{total_size / 1024:,.2f} KB '
                        f'({percent_complete:.2f}%)', end='\r'
                        )

    if vb:
        print(
            f'\nDownload complete: {downloaded_size / 1024:,.2f} KB downloaded.'
            )

    return local_filename
