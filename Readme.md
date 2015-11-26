script.colorbox

- Available operations:
  twotone: will grayscale the image then replace black and white with colors of choice (or default grayscale if none supplied)
  posterize: will downgrade image to bit level of choice
  pixelate: will bulk up pixels to size requested and add black border round each pixel block
  blur: will return a guassian blurred image dependant on radius supplied, larger radius means larger blur
  randomcolor: will return a random color

- Notes:
  On first use it will check and make addon cache dir
  First run of an image will be slow as it is processing image, then all other calls will use a cached image for extra speed


- Usage:
  RunScript(script.colorbox,info=twotone,id='"IMAGE_TO_USE"',black='"1ST_COLOR"',white='"2ND_COLOR"',prefix=RETURN_IMAGE_ID)
  RunScript(script.colorbox,info=posterize,id='"IMAGE_TO_USE"',bits=BIT_SIZE,prefix=RETURN_IMAGE_ID)
  RunScript(script.colorbox,info=pixelate,id='"IMAGE_TO_USE"',pixels=PIXELATION_SIZE,prefix=RETURN_IMAGE_ID)
  RunScript(script.colorbox,info=blur,id='"IMAGE_TO_USE"',radius=RADIUS_SIZE,prefix=RETURN_IMAGE_ID)
  RunScript(script.colorbox,info=randomcolor,prefix=RETURN_IMAGE_ID)

- Vars:
  IMAGE_TO_USE        Image to be manipulated
  RETURN_IMAGE_ID     Image returned will be available as a window property (see below)
  1ST_COLOR           Color to replace the black pixels in format #000000
  2ND_COLOR           Color to replace the white pixels in format #000000
  BIT_SIZE            1,2,3,4,5,6,7,8
  PIXELATION_SIZE     1-infinity, though 1 will return a 1:1 copy!
  RADIUS_SIZE         The larger the more blurred the returned image

- Window properties:
  Window(home).Property(RETURN_IMAGE_ID.Image)
  Window(home).Property(RETURN_IMAGE_ID.ImageColor) <- only available with 'blur' and 'randomcolor'
