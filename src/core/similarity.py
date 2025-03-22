import numpy as np

def calculate_similarity(new_image, original_image, sensitivity):
    """
    Calculate similarity percentage between two images based on pixel difference.
    
    Args:
        new_image (numpy.ndarray): Processed image
        original_image (numpy.ndarray): Original image
        sensitivity (int): Sensitivity value (1, 2, 4, 16, 32, 64, 128, 255)
        
    Returns:
        int: Similarity percentage (0-100)
    """
    list1 = new_image.tolist()
    size1 = new_image.size
    x = len(list1)
    y = int(size1/x)
    counter = 0
    range1 = round(255/(int(sensitivity)))
    list2 = original_image.tolist()
    
    for i in range(0, x):
        for j in range(0, y):
            originalp = list2[i][j]
            newp = list1[i][j]
            if(originalp + range1 >= newp and originalp - range1 <= newp):
                counter += 1
                
    return round(counter * 100 / (x * y))