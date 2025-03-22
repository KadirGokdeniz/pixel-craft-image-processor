from src.core.filters import ImageFilters
from src.core.similarity import calculate_similarity
from src.utils.image_io import ImageIO

def process_image(image_name, filter_name, sensitivity):
    """
    Process an image with the specified filter and calculate similarity.
    
    Args:
        image_name (str): Name of the image file (without extension)
        filter_name (str): Name of the filter to apply
        sensitivity (int): Sensitivity value for similarity calculation
        
    Returns:
        int: Similarity percentage
    """
    # File path construction (this should be configurable in production)
    image_path = f"resources/images/{image_name}.jpg"
    
    # Load the original image
    original = ImageIO.read_image(image_path)
    
    # Make a copy for processing
    processed = original.copy()
    
    # Apply the selected filter
    filters = ImageFilters()
    if filter_name.lower() == "average":
        processed = filters.average_filter(processed)
    elif filter_name.lower() == "sharpen":
        processed = filters.sharpen_filter(processed)
    elif filter_name.lower() == "negative":
        processed = filters.negative_filter(processed)
    elif filter_name.lower() == "laplacian":
        processed = filters.laplacian_filter(processed)
    elif filter_name.lower() == "logarithm":
        processed = filters.logarithm_filter(processed)
    else:
        raise ValueError(f"Unsupported filter: {filter_name}")
    
    # Display the images
    ImageIO.display_image(original, "Original")
    ImageIO.display_image(processed, f"{filter_name} Filter")
    
    # Calculate similarity
    similarity = calculate_similarity(processed, original, sensitivity)
    
    return similarity