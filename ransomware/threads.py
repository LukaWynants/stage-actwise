import psutil

def determine_thread_count():
    """Determines optimal thread count based on system specs."""
    
    cpu_count = psutil.cpu_count(logical=True)  # Logical cores
    phys_cores = psutil.cpu_count(logical=False)  # Physical cores
    cpu_load = psutil.cpu_percent(interval=1)  # Current CPU usage %
    mem = psutil.virtual_memory()  # Get RAM info
    
    # Default thread count: Use 80% of available logical cores
    thread_count = max(1, int(cpu_count * 0.8))

    # If system is under high load (CPU > 70% or RAM < 1GB free), reduce threads
    if cpu_load > 70 or mem.available < 1 * 1024**3:
        thread_count = max(1, thread_count // 2)

    # Cap threads at physical core count if low on resources
    if cpu_load > 85 or mem.available < 512 * 1024**2:
        thread_count = max(1, phys_cores)

    return thread_count

# Example usage:
optimal_threads = determine_thread_count()
print(f"Optimal thread count: {optimal_threads}")

determine_thread_count()