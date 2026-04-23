def stringify(data : dict[str,str]):
    items = [] 
    for key, value in data.items():
        items.append(f"{key}={value}")
    return "&".join(items)