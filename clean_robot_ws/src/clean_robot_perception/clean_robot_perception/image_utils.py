import numpy as np


class ImageConversionError(ValueError):
    pass


class ImageUtils:

    @staticmethod
    def bbox_center(x, y, width, height):

        cx = x + width / 2.0

        cy = y + height / 2.0

        return cx, cy

    @staticmethod
    def image_msg_to_numpy(image_msg):
        encoding = (image_msg.encoding or '').lower()
        dtype, channels = ImageUtils._encoding_info(encoding)

        item_size = dtype.itemsize
        if image_msg.step < image_msg.width * channels * item_size:
            raise ImageConversionError(
                f'Invalid image step={image_msg.step} for '
                f'{image_msg.width}x{image_msg.height} {image_msg.encoding}'
            )

        buffer_dtype = dtype
        if item_size > 1:
            byte_order = '>' if image_msg.is_bigendian else '<'
            buffer_dtype = dtype.newbyteorder(byte_order)

        data = np.frombuffer(image_msg.data, dtype=buffer_dtype)
        row_values = image_msg.step // item_size
        required_values = row_values * image_msg.height
        if data.size < required_values:
            raise ImageConversionError(
                f'Image data is too small: got {data.size}, '
                f'need {required_values} values'
            )

        rows = data[:required_values].reshape(
            image_msg.height,
            row_values
        )
        valid_values = image_msg.width * channels
        image = rows[:, :valid_values]

        if channels == 1:
            image = image.reshape(image_msg.height, image_msg.width)
        else:
            image = image.reshape(
                image_msg.height,
                image_msg.width,
                channels
            )

        if image.dtype != dtype:
            image = image.astype(dtype, copy=False)

        return np.ascontiguousarray(image)

    @staticmethod
    def to_bgr8(image_msg):
        image = ImageUtils.image_msg_to_numpy(image_msg)
        encoding = (image_msg.encoding or '').lower()

        if encoding == 'bgr8':
            return image

        if encoding == 'rgb8':
            return np.ascontiguousarray(image[:, :, ::-1])

        if encoding == 'bgra8':
            return np.ascontiguousarray(image[:, :, :3])

        if encoding == 'rgba8':
            return np.ascontiguousarray(image[:, :, [2, 1, 0]])

        if encoding in ('mono8', '8uc1'):
            return np.repeat(image[:, :, None], 3, axis=2)

        raise ImageConversionError(
            f'Unsupported color image encoding: {image_msg.encoding}'
        )

    @staticmethod
    def _encoding_info(encoding):
        encodings = {
            'bgr8': (np.dtype(np.uint8), 3),
            'rgb8': (np.dtype(np.uint8), 3),
            'bgra8': (np.dtype(np.uint8), 4),
            'rgba8': (np.dtype(np.uint8), 4),
            'mono8': (np.dtype(np.uint8), 1),
            '8uc1': (np.dtype(np.uint8), 1),
            '8uc3': (np.dtype(np.uint8), 3),
            '8uc4': (np.dtype(np.uint8), 4),
            'mono16': (np.dtype(np.uint16), 1),
            '16uc1': (np.dtype(np.uint16), 1),
            '32fc1': (np.dtype(np.float32), 1),
            '64fc1': (np.dtype(np.float64), 1),
        }

        if encoding not in encodings:
            raise ImageConversionError(
                f'Unsupported image encoding: {encoding}'
            )

        return encodings[encoding]
