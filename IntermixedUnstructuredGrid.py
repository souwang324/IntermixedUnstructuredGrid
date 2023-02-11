

#!/usr/bin/env python

# noinspection PyUnresolvedReferences
import vtk
import vtkmodules.vtkInteractionStyle
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkPiecewiseFunction
from vtkmodules.vtkImagingHybrid import vtkSampleFunction
from vtkmodules.vtkIOLegacy import vtkStructuredPointsReader
from vtkmodules.vtkFiltersCore import vtkThreshold
from vtkmodules.vtkFiltersCore import vtkContourFilter
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkImageData
from vtkmodules.vtkIOImage import vtkDICOMImageReader
from vtkmodules.vtkFiltersGeometry import vtkImageDataGeometryFilter
from vtkmodules.vtkIOXML import vtkXMLImageDataReader
#from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkIOImage import vtkMetaImageReader
from vtkmodules.vtkCommonCore import vtkStringArray
from vtkmodules.vtkCommonDataModel import (
    vtkCylinder,
    vtkSphere
)
from vtkmodules.vtkImagingCore import (
  vtkImageCast,
  vtkImageShiftScale
)
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCamera,
    vtkPolyDataMapper,
    vtkColorTransferFunction,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer,
    vtkVolume,
    vtkVolumeProperty
)


from vtkmodules.vtkRenderingVolume import vtkFixedPointVolumeRayCastMapper
# noinspection PyUnresolvedReferences
from vtkmodules.vtkRenderingVolumeOpenGL2 import vtkOpenGLRayCastImageDisplayHelper
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera

def get_program_parameters():
  import argparse
  description = 'Read a VTK image data file.'
  epilogue = ''''''
  parser = argparse.ArgumentParser(description=description, epilog=epilogue,
                                   formatter_class=argparse.RawDescriptionHelpFormatter)
  parser.add_argument('filename1', help='ironProt.vtk')
  parser.add_argument('filename2', help='neghip.slc')
  args = parser.parse_args()
  return args.filename1, args.filename2



def main():
  # Create the reader for the data
  # This is the data the will be volume rendered
  filename1, filename2 = get_program_parameters()
  reader = vtkStructuredPointsReader()
  reader.SetFileName(filename1)

  # create a reader for the other data that will
  # be contoured and displayed as a polygonal mesh
  reader2 = vtk.vtkSLCReader()
  reader2.SetFileName(filename2)

  # convert from vtkImageData to vtkUnstructuredGrid, remove
  # any cells where all values are below 80
  thresh = vtkThreshold()
  thresh.SetUpperThreshold(80)
  thresh.SetThresholdFunction(vtkThreshold.THRESHOLD_UPPER)
  # thresh.ThresholdByUpper(80)
  thresh.AllScalarsOff()
  thresh.SetInputConnection(reader.GetOutputPort())

  trifilter = vtk.vtkDataSetTriangleFilter()
  trifilter.SetInputConnection(thresh.GetOutputPort())

  # Create transfer mapping scalar value to opacity
  opacityTransferFunction = vtkPiecewiseFunction()
  opacityTransferFunction.AddPoint(80, 0.0)
  opacityTransferFunction.AddPoint(120, 0.2)
  opacityTransferFunction.AddPoint(255, 0.2)

  # Create transfer mapping scalar value to color
  colorTransferFunction = vtkColorTransferFunction()
  colorTransferFunction.AddRGBPoint(80.0, 0.0, 0.0, 0.0)
  colorTransferFunction.AddRGBPoint(120.0, 0.0, 0.0, 1.0)
  colorTransferFunction.AddRGBPoint(160.0, 1.0, 0.0, 0.0)
  colorTransferFunction.AddRGBPoint(200.0, 0.0, 1.0, 0.0)
  colorTransferFunction.AddRGBPoint(255.0, 0.0, 1.0, 1.0)

  # The property describes how the data will look
  volumeProperty = vtkVolumeProperty()
  volumeProperty.SetColor(colorTransferFunction)
  volumeProperty.SetScalarOpacity(opacityTransferFunction)
  volumeProperty.ShadeOff()
  volumeProperty.SetInterpolationTypeToLinear()

  # The mapper / ray cast function know how to render the data
  volumeMapper = vtk.vtkUnstructuredGridVolumeRayCastMapper()
  volumeMapper.SetInputConnection(trifilter.GetOutputPort())

  renWin = vtkRenderWindow()
  renWin.SetSize(640, 512)
  ren1 = vtkRenderer()

  # contour the second dataset
  contour = vtkContourFilter()
  contour.SetValue(0, 80)
  contour.SetInputConnection(reader2.GetOutputPort())

  # create a mapper for the polygonal data
  mapper = vtkPolyDataMapper()
  mapper.SetInputConnection(contour.GetOutputPort())
  mapper.ScalarVisibilityOff()

  # create an actor for the polygonal data
  actor = vtkActor()
  actor.SetMapper(mapper)

  ren1.AddViewProp(actor)

  ren1.SetBackground(0.1, 0.4, 0.2)

  renWin.AddRenderer(ren1)
  renWin.SetWindowName("IntermixedUnstructuredGrid")

  iren = vtkRenderWindowInteractor()
  iren.SetRenderWindow(renWin)

  volume = vtkVolume()
  volume.SetMapper(volumeMapper)
  volume.SetProperty(volumeProperty)

  ren1.AddVolume(volume)

  ren1.ResetCamera()
  ren1.GetActiveCamera().Zoom(1.5)

  # Render composite. In default mode. For coverage.
  renWin.Render()

  iren.Start()

if __name__ == '__main__':
    main()