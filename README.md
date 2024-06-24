# phelix
Line6 Helix preset generator

## Description

Generates random presets for Helix processors, and enables you to mutate your own presets to search for unusual sounds.

## Usage

In a terminal, go to the phelix folder and run `python3 gui.py`.
There will be some basic settings already loaded.  Click "Generate" at the bottom of the controls.  With luck, 5 new presets can now be found in the presets/generated folder.  Now you can use HXedit to import these to your Helix.  
There's a chance one or more of the presets will be blank.  I think this happens if the preset would use too much processing, and so the Helix counts it invalid.  Great, the Helix didn't break!

## File Structure

-blocks/ contains the blocks that have been exported from a Helix which phelix loads to construct a new preset. So far these are (almost all) mono and legacy, but this might change (you can add any if you find them missing).  The blocks are made using HXedit by snapshotting all parameters (except bypass)

-presets/
    -generated/ holds generated presets
    -templates/ has template presets which phelix modifies by swapping blocks from the blocks folder. The one called LessOccSplit.hlx has 5 blocks on each dsp, and uses all the paths.  This seems a fairly reliable number of blocks before the presets fail to load, since phelix doesn't account for more and less dsp intensive effects.  That said, phelix limits Amp/Cab combos to one per dsp (though they may mutate beyond that... I have to check)



## Contributing

Contributions to enhance the block rearrangement functionality or improve the code structure are welcome. Please follow the docstring guidelines and maintain code quality.

## License

Specify the project's license.

## Contact Information

For questions or feedback, contact [Your Name] at [Your Email].
