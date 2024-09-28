# ecoscope-workflows

## Structure

```
.
├── dev
│   └── ...
├── examples
│   └── ...
├── pixi.lock
├── pixi.toml
├── publish
│   └── ...
└── src
    ├── ecoscope-workflows-core
    └── ecoscope-workflows-ext-ecoscope
```

## Development

## Why pixi?

| feature            | pip | poetry | conda | mamba | micromamba | pixi.sh |
| ---------------    | --- | ------ | ----- | ----- | ---------- | ------- |
| python deps        |  ✅ |   ✅   | ✅    | ✅    | ✅         |  ✅     |
| conda-compatible   |  ❌ |   ❌   | ✅    | ✅    | ✅         |  ✅     |
| native lockfiles   |  ❌ |   ✅   | ❌    | ❌    | ❌         |  ✅     |
| performance        |  ✅ |   ✅   | ❌    | 🤷    | 🤷         |  🔥     |


## Examples

To recompile all examples in the `examples/` directory

1. [Install pixi](https://pixi.sh/latest/#installation)
2. From the repo root, run:
    ```console
    $ pixi run --manifest-path pixi.toml recompile-all
    ```
