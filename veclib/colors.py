'''
matplotlib ref:
https://matplotlib.org/stable/tutorials/colors/colormaps.html
https://stackoverflow.com/questions/25408393/getting-individual-colors-from-a-color-map-in-matplotlib
'''
import matplotlib

def colormap_interpret(vmin=0, vmax=1, v=0.5, colormap='Spectral'):
    '''
    rgba = colormap_interpret(vmin=0, vmax=1, v=0.5, colormap='Spectral')
    :param vmin:
    :param vmax:
    :param v:
    :param colormap: https://matplotlib.org/stable/tutorials/colors/colormaps.html#diverging
    :return: rgba
    '''

    norm = matplotlib.colors.Normalize(vmin, vmax)
    cmap = matplotlib.cm.get_cmap(colormap)
    rgba = cmap(norm(v), bytes=True)
    rgba = [int(i) for i in rgba]

    return rgba


