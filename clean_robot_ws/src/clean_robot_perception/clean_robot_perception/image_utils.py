class ImageUtils:

    @staticmethod
    def bbox_center(x, y, width, height):

        cx = x + width / 2.0

        cy = y + height / 2.0

        return cx, cy