from numpy.random import SeedSequence, default_rng
import time

def generate_seeds(Nseeds, master_seed=None, seed_bounds=(0, 2**32-1),
                   return_master=False):
    '''
    generate a set of safe, independent seeds given a master seed

    Nseeds: int
        The number of desired independent seeds
    master_seed: int
        A seed that initializes the SeedSequence, if desired
    seed_bounds: tuple of ints
        The min & max values for the seeds to be sampled from
    return_master: bool
        Return the master seed as well (in case it wasn't passed!)
    '''

    if (not isinstance(Nseeds, int)) or (Nseeds < 1):
        raise ValueError('Nseeds must be a positive int!')

    for b in seed_bounds:
        if not isinstance(b, int):
            raise TypeError('seed_bounds must be a tuple of ints!')
        if seed_bounds[0] < 0:
            raise ValueError('seed_bounds must be positive!')
        if seed_bounds[1] < seed_bounds[0]:
            raise ValueError('seed_bounds values must be monotonic!')

    if master_seed is None:
        # local time in microseconds
        master_seed = int(time.time()*1e6)

    ss = SeedSequence(master_seed)
    child_seeds = ss.spawn(Nseeds)
    streams = [default_rng(s) for s in child_seeds]

    seeds = []
    for k in range(Nseeds):
        val = int(streams[k].integers(seed_bounds[0], seed_bounds[1]))
        seeds.append(val)

    if return_master is True:
        return seeds, master_seed
    else:
        return seeds
