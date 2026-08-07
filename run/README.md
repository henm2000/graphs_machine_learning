# How Google Drive works in this project

Read this once. It applies to all four of you.

## The short version

There are **two** folders in your Drive, and you only ever create one of them.

```
My Drive/
  person1/          <- YOU create this. Just the notebooks. Nothing is written here.
  trpe/             <- CREATED AUTOMATICALLY the first time you run a notebook.
                       All results land here.
```

If you have already uploaded your `personN/` folder, **your setup is finished.** Open a
notebook, set the GPU runtime, and run it. `trpe/` will appear in your Drive by itself.

---

## Why there are two folders

The notebooks are **self-contained** — they don't read anything from the folder they sit in, and
they don't import from each other. So `person1/` is nothing more than a place for the `.ipynb`
files to live so Colab can open them. You could rename it, move it, or nest it inside another
folder and nothing would change.

`trpe/` is the output. Every notebook mounts your Drive, creates `trpe/` if it isn't there, and
writes its results into it. That is the entire mechanism.

There is also a third location, `/content/trpe_data`, which holds the downloaded datasets. That
one is **not** in your Drive — it lives on the Colab machine and is wiped when your session
ends, so the datasets re-download each session. That is deliberate: they are a gigabyte or more
and they are freely re-downloadable, so keeping them out of your Drive quota is the right trade.
You never touch this folder.

---

## What appears in `trpe/`, and when

```
My Drive/trpe/
  results/
    gcn/CSL/        M0_seed0_fold0.json, M0_seed0_fold1.json, ...
    gcn/CLUSTER/    M0_seed0.json, M0_seed1.json, ...
    gcn/CIFAR10/    M0_seed0.json, ...
    expressivity/   expressivity.json        (from shared/01)
    efficiency/     efficiency.json          (from shared/06)
    ablations/      r1_seed0.json, r2_seed0.json, ...   (from shared/05)
  figures/          fig_distance_profile.pdf, fig_efficiency.pdf, ...
  paper_tables/     table1_main.tex          (from shared/07)
```

**One JSON file per run.** CSL uses 4 seeds × 5 cross-validation folds, so a CSL notebook writes
20 files; CLUSTER writes 3 (one per seed) and CIFAR10-SP writes 1. This is not clutter — it is
what makes the runs resumable. When a notebook starts, it checks which files already exist and
skips those runs. That is why a dropped Colab session costs you one run instead of a whole
notebook, and it is why four people can work at once without coordinating.

**Do not rename, move, or tidy anything inside `trpe/` while you are still running notebooks.**
The skip-if-exists check reads those exact paths. Moving a file makes that run happen again.

---

## Where the results go at the end

Each of you mounts **your own** Drive, so there will be four separate `trpe/` folders — one per
person, each holding only your share. They have to be combined before the final collection
notebook can build the tables.

**Persons 2, 3 and 4:** when you finish, right-click your `trpe` folder in Drive →
**Download**. Drive gives you a `.zip`. Send it to Person 1.

**Person 1:** unzip all three next to your own `trpe/results/` and merge them. The four shares
never write the same filename, so nothing can overwrite anything — but the folders *do* overlap.
For example `results/gcn/CIFAR10/` gets `M0`, `M1` from you and `M2`, `M3`, `M4` from Person 3,
and `results/ablations/` gets four files from Person 3 and four from Person 4.

So merge **contents into** existing folders rather than replacing folders wholesale. The reliable
way is to do it on your own computer — unzip everything, drag the folders together (Windows and
macOS both merge same-named folders and only prompt on identical filenames, and there are none),
then upload the merged `trpe/results/` back to your Drive, replacing what's there.

Then run `shared/07_results_and_figures.ipynb`. Its **last cell prints a grid showing how many
runs landed in every cell**, so if a merge went wrong or someone missed a notebook, you will see
a zero rather than a quietly missing row.

### If dragging folders around sounds fragile

It is. The alternative: each of Persons 2–4 right-clicks their `trpe` folder → **Share** → shares
it with Person 1's Google account. Person 1 then adds it as a shortcut in their own Drive and
copies it across with a Colab cell:

```python
!cp -rn "/content/drive/MyDrive/trpe_person2/results/." "/content/drive/MyDrive/trpe/results/"
```

`cp -rn` merges directories and never overwrites an existing file, which is exactly the
behaviour you want here.

---

## Quick checklist

* [ ] `personN/` folder uploaded to your Drive — **this is your only setup step**
* [ ] Open a notebook → *Open with → Google Colaboratory*
* [ ] **Runtime → Change runtime type → T4 GPU** (resets every session, check it each time)
* [ ] **Runtime → Run all**, approve the Drive-mount prompt
* [ ] Confirm `trpe/` appeared in your Drive after the first notebook
* [ ] Don't touch anything inside `trpe/` while runs are ongoing
* [ ] When finished: download `trpe/` as a zip and send it to Person 1

## Common confusions

| | |
|---|---|
| "I don't see `trpe/` in my Drive" | It appears after the first notebook mounts Drive and reaches its results cell. If a notebook errored before that, `trpe/` won't exist yet. |
| "It's asking me to authorise Drive again" | Normal — Colab re-asks each new session. |
| "The dataset downloaded again" | Expected. Datasets live on the Colab machine, not your Drive. |
| "I re-ran a notebook and it finished instantly" | Working as intended: every run already had its JSON file, so all were skipped. |
| "I want to redo a run" | Delete that run's JSON file from `trpe/results/...` and re-run the notebook. |
| "Do I need the whole `project/` folder in Drive?" | No. Only your `personN/` folder. The notebooks are self-contained. |
