#include "BoundingBox.h"

/// Constructor.
/// \param[in]  top_left_position - A vector representing the x and y values of the top-left position for this box.
/// \param[in]  dimensions - A vector representing the height and width of the box.
/// \author CJ Harper
/// \date   04/28/2019
BoundingBox::BoundingBox(const sf::Vector2<float>& top_left_position, const sf::Vector2<float>& dimensions):
TopLeftCoordinate(top_left_position),
BottomLeftCoordinate(),
TopRightCoordinate(),
BottomRightCoordinate(),
Width(dimensions.x),
Height(dimensions.y)
{
    // DETERMINE THE BOUNDARIES FOR THIS BOX.
    const float box_height = dimensions.y;
    const float lowest_y_coordinate_of_box = (top_left_position.y + box_height);
    BottomLeftCoordinate = sf::Vector2<float>(top_left_position.x, lowest_y_coordinate_of_box);
    const float box_width = dimensions.x;
    const float right_most_x_coordinate_of_box = (top_left_position.x + box_width);
    TopRightCoordinate = sf::Vector2<float>(right_most_x_coordinate_of_box, top_left_position.y);
    BottomRightCoordinate = sf::Vector2<float>(right_most_x_coordinate_of_box, lowest_y_coordinate_of_box);
}

/// Translates the box a set distance.
/// \param[in]	translation - The amount to translate the box by.
/// \author	CJ Harper
/// \date	04/28/2019
void BoundingBox::Translate(const sf::Vector2<float>& translation)
{
	// TRANSLATE THE BOX TO THE NEW POSITION.
	TopLeftCoordinate.x += translation.x;
	TopLeftCoordinate.y += translation.y;
	BottomLeftCoordinate.x += translation.x;
	BottomLeftCoordinate.y += translation.y;
	TopRightCoordinate.x += translation.x;
	TopRightCoordinate.y += translation.y;
	BottomRightCoordinate.x += translation.x;
	BottomRightCoordinate.y += translation.y;
}

/// Sets a new posistion for this box.
/// \param[in]	new_top_left_position - The new position of the top-left coordinate of this box.
/// \author	CJ Harper
/// \date	04/28/2019
void BoundingBox::SetPosition(const sf::Vector2<float>& new_top_left_position)
{
	// DETERMINE HOW MUCH THIS BOX NEEDS TO TRANSLATE TO GET TO THE NEW POSITION.
	const float x_translation = new_top_left_position.x - TopLeftCoordinate.x;
	const float y_translation = new_top_left_position.y - TopLeftCoordinate.y;
	sf::Vector2<float> translation(x_translation, y_translation);

	// TRANSLATE THE BOX TO THE NEW POSITION.
	Translate(translation);
}

/// Checks if another box is colliding with this one.
/// \param[in]  other - The other box to check for collisions with.
/// \return True if a collision is happening. False otherwise.
/// \author CJ Harper
/// \date   04/28/2019
bool BoundingBox::CheckCollision(const BoundingBox& other) const
{
    // DETERMINE IF THE OTHER BOX IS COLLIDING WITH THIS ONE.
    // A collision is assumed if any corners of the other box are inside this one.
    const bool other_box_top_left_coordinate_inside_this_box = CheckIfContainsCoordinate(other.TopLeftCoordinate);
    const bool other_box_top_right_coordinate_inside_this_box = CheckIfContainsCoordinate(other.TopRightCoordinate);
    const bool other_box_bottom_left_coordinate_inside_this_box = CheckIfContainsCoordinate(other.BottomLeftCoordinate);
    const bool other_box_bottom_right_coordinate_inside_this_box = CheckIfContainsCoordinate(other.BottomRightCoordinate);
    const bool collision = (
        other_box_top_left_coordinate_inside_this_box || 
        other_box_top_right_coordinate_inside_this_box || 
        other_box_bottom_left_coordinate_inside_this_box || 
        other_box_bottom_right_coordinate_inside_this_box);
        
    return collision;
}

/// Determines if this box contains the specified coordinate.
/// \param[in]  coordinate - The coordinate to check whether this box contains.
/// \return True if the box contains the coordinate. False otherwise.
/// \author CJ Harper
/// \date   04/28/2019
bool BoundingBox::CheckIfContainsCoordinate(const sf::Vector2<float>& coordinate) const
{
    const bool x_coordinate_inside_box = (TopLeftCoordinate.x < coordinate.x && coordinate.x < TopRightCoordinate.x);
    const bool y_coordinate_inside_box = (TopLeftCoordinate.y < coordinate.y && coordinate.y < BottomLeftCoordinate.y);
    const bool box_contains_coordinate = (x_coordinate_inside_box && y_coordinate_inside_box);
    
    return box_contains_coordinate;
}