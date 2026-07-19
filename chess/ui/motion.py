def get_smooth_position(engine, row, col):
    """Calculate smooth interpolated position for a piece during movement.
    
    Args:
        engine: GameEngine instance
        row: Piece row
        col: Piece column
    
    Returns:
        Tuple (smooth_row, smooth_col) with interpolated position
    """
    cmd = engine.get_move_command(row, col)
    if cmd is None:
        return (row, col)
    
    # Get current and target positions
    from_row, from_col = cmd.from_row, cmd.from_col
    to_row, to_col = cmd.current_row, cmd.current_col
    
    # Find progress between checkpoints
    checkpoints = cmd.checkpoints
    if not checkpoints:
        return (to_row, to_col)
    
    # Find which segment we're in
    prev_checkpoint = None
    next_checkpoint = None
    for i, (due_time, r, c) in enumerate(checkpoints):
        if due_time <= cmd.elapsed:
            prev_checkpoint = (due_time, r, c)
        else:
            next_checkpoint = (due_time, r, c)
            break
    
    # If no next checkpoint, return current position
    if next_checkpoint is None:
        return (to_row, to_col)
    
    # If no prev checkpoint, start from origin
    if prev_checkpoint is None:
        prev_time, prev_r, prev_c = 0, from_row, from_col
    else:
        prev_time, prev_r, prev_c = prev_checkpoint
    
    next_time, next_r, next_c = next_checkpoint
    
    # Calculate progress in this segment
    time_in_segment = cmd.elapsed - prev_time
    segment_duration = next_time - prev_time
    
    if segment_duration <= 0:
        return (prev_r, prev_c)
    
    progress = min(1.0, time_in_segment / segment_duration)
    
    # Linear interpolation
    smooth_row = prev_r + (next_r - prev_r) * progress
    smooth_col = prev_c + (next_c - prev_c) * progress
    
    return (smooth_row, smooth_col)
