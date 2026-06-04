"""
See COPYRIGHT.md for copyright information.
"""
from __future__ import annotations

from collections.abc import Mapping, Set
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any

from arelle.utils.mapping.compressed_trie import CompressedTrie


@dataclass(frozen=True)
class PackageMeta:
    description: str | None
    entry_points: Mapping[str, Set[tuple[str, str, str]]] # Path, URL, Description
    file_date: str | None
    identifier: str | None
    license: str | None
    manifest_name: str | None
    name: str | None
    publication_date: str | None
    publisher: str | None
    publisher_country: str | None
    publisher_url: str | None
    remappings: CompressedTrie
    status: str | None
    superseded_taxonomy_packages: Set[str]
    url: str
    version: str | None
    versioning_reports: Set[str]

    @staticmethod
    def from_config(config: dict[str, Any]) -> PackageMeta:
        return PackageMeta(
            description=config.get("description"),
            entry_points=MappingProxyType({
                name: frozenset(
                    (path, url, description)
                    for path, url, description in entry_points
                )
                for name, entry_points in config.get("entryPoints", {}).items()
            }),
            file_date=config.get("fileDate"),
            identifier=config.get("identifier"),
            license=config.get("license"),
            manifest_name=config.get("manifestName"),
            name=config.get("name"),
            publication_date=config.get("publicationDate"),
            publisher=config.get("publisher"),
            publisher_country=config.get("publisherCountry"),
            publisher_url=config.get("publisherURL"),
            remappings=CompressedTrie().load_from_dict(config.get("remappings", CompressedTrie()).to_dict()), # copy content
            status=config.get("status"),
            superseded_taxonomy_packages=frozenset(config.get("supersededTaxonomyPackages", [])),
            url=config.get("URL") or "",
            version=config.get("version"),
            versioning_reports=frozenset(config.get("versioningReports", [])),
        )
