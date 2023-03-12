'''
TODO:
    Each layer needs to specify the following
    1. id: A number representing a particular layer
    2. name: The name of the layer. Does not necessarily have to be the same as the directory name containing the layer images.
    3. directory: The folder inside assets that contain traits for the particular layer
    4. required: If the particular layer is required (True) or optional (False). The first layer must always be set to true.
    5. rarity_weights: Denotes the rarity distribution of traits. It can take on three types of values.
        - None: This makes all the traits defined in the layer equally rare (or common)
        - "random": Assigns rarity weights at random. 
        - array: An array of numbers where each number represents a weight. 
                If required is True, this array must be equal to the number of images in the layer directory. The first number is  the weight of the first image (in alphabetical order) and so on...
                If required is False, this array must be equal to one plus the number of images in the layer directory. The first number is the weight of having no image at all for this layer. The second number is the weight of the first image and so on...

'''

CONFIG=[
    ''' 
    NOTE :
        -- First folder layers configs (must contains layers)
        -- 'ex_1' according to main.py script
        -- dictionary depends on layers inside folder

        syntax for dictionary
            {
                'id': " 1, 2, 3, etc.",
                'name': 'Name it',
                'directory': 'layer folder name',
                'required': True,
                'rarity_weights': None,
            },
    '''
    [
        {
        'id': 1,
        'name': 'background',
        'directory': 'Background',
        'required': True,
        'rarity_weights': None,
    },
    {
        'id': 2,
        'name': 'face',
        'directory': 'Face',
        'required': True,
        'rarity_weights': None,
    },
    ],

    ''' 
    NOTE :
        second folder layers configs
        'ex_2' according to main.py script
    '''
    [
        {
        'id': 1,
        'name': 'background',
        'directory': 'Background',
        'required': True,
        'rarity_weights': None,
    },
    {
        'id': 2,
        'name': 'face',
        'directory': 'Face',
        'required': True,
        'rarity_weights': None,
    },
    ]
]
