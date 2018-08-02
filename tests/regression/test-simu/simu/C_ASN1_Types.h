#ifndef __C_DATAVIEW_UNIQ_H__
#define __C_DATAVIEW_UNIQ_H__

#include <stdlib.h> /* for size_t */

#include "dataview-uniq.h" // Space certified compiler generated

#include "../../system_config.h" // Choose ASN.1 Types to use

#ifdef __NEED_MyChoice_UPER
size_t Encode_UPER_MyChoice(void *pBuffer, size_t iMaxBufferSize, const asn1SccMyChoice *pSrc);
#endif

#ifdef __NEED_MyChoice_ACN
size_t Encode_ACN_MyChoice(void *pBuffer, size_t iMaxBufferSize, asn1SccMyChoice *pSrc);
#endif

#ifdef __NEED_MyChoice_NATIVE
size_t Encode_NATIVE_MyChoice(void *pBuffer, size_t iMaxBufferSize, const asn1SccMyChoice *pSrc);
#endif

#ifdef __NEED_MyChoice_UPER
int Decode_UPER_MyChoice(asn1SccMyChoice *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MyChoice_ACN
int Decode_ACN_MyChoice(asn1SccMyChoice *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MyChoice_NATIVE
int Decode_NATIVE_MyChoice(asn1SccMyChoice *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_TASTE_Peek_id_list_UPER
size_t Encode_UPER_TASTE_Peek_id_list(void *pBuffer, size_t iMaxBufferSize, const asn1SccTASTE_Peek_id_list *pSrc);
#endif

#ifdef __NEED_TASTE_Peek_id_list_ACN
size_t Encode_ACN_TASTE_Peek_id_list(void *pBuffer, size_t iMaxBufferSize, asn1SccTASTE_Peek_id_list *pSrc);
#endif

#ifdef __NEED_TASTE_Peek_id_list_NATIVE
size_t Encode_NATIVE_TASTE_Peek_id_list(void *pBuffer, size_t iMaxBufferSize, const asn1SccTASTE_Peek_id_list *pSrc);
#endif

#ifdef __NEED_TASTE_Peek_id_list_UPER
int Decode_UPER_TASTE_Peek_id_list(asn1SccTASTE_Peek_id_list *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_TASTE_Peek_id_list_ACN
int Decode_ACN_TASTE_Peek_id_list(asn1SccTASTE_Peek_id_list *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_TASTE_Peek_id_list_NATIVE
int Decode_NATIVE_TASTE_Peek_id_list(asn1SccTASTE_Peek_id_list *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySetOf_UPER
size_t Encode_UPER_MySetOf(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySetOf *pSrc);
#endif

#ifdef __NEED_MySetOf_ACN
size_t Encode_ACN_MySetOf(void *pBuffer, size_t iMaxBufferSize, asn1SccMySetOf *pSrc);
#endif

#ifdef __NEED_MySetOf_NATIVE
size_t Encode_NATIVE_MySetOf(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySetOf *pSrc);
#endif

#ifdef __NEED_MySetOf_UPER
int Decode_UPER_MySetOf(asn1SccMySetOf *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySetOf_ACN
int Decode_ACN_MySetOf(asn1SccMySetOf *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySetOf_NATIVE
int Decode_NATIVE_MySetOf(asn1SccMySetOf *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MyEnum_UPER
size_t Encode_UPER_MyEnum(void *pBuffer, size_t iMaxBufferSize, const asn1SccMyEnum *pSrc);
#endif

#ifdef __NEED_MyEnum_ACN
size_t Encode_ACN_MyEnum(void *pBuffer, size_t iMaxBufferSize, asn1SccMyEnum *pSrc);
#endif

#ifdef __NEED_MyEnum_NATIVE
size_t Encode_NATIVE_MyEnum(void *pBuffer, size_t iMaxBufferSize, const asn1SccMyEnum *pSrc);
#endif

#ifdef __NEED_MyEnum_UPER
int Decode_UPER_MyEnum(asn1SccMyEnum *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MyEnum_ACN
int Decode_ACN_MyEnum(asn1SccMyEnum *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MyEnum_NATIVE
int Decode_NATIVE_MyEnum(asn1SccMyEnum *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_TASTE_Peek_id_UPER
size_t Encode_UPER_TASTE_Peek_id(void *pBuffer, size_t iMaxBufferSize, const asn1SccTASTE_Peek_id *pSrc);
#endif

#ifdef __NEED_TASTE_Peek_id_ACN
size_t Encode_ACN_TASTE_Peek_id(void *pBuffer, size_t iMaxBufferSize, asn1SccTASTE_Peek_id *pSrc);
#endif

#ifdef __NEED_TASTE_Peek_id_NATIVE
size_t Encode_NATIVE_TASTE_Peek_id(void *pBuffer, size_t iMaxBufferSize, const asn1SccTASTE_Peek_id *pSrc);
#endif

#ifdef __NEED_TASTE_Peek_id_UPER
int Decode_UPER_TASTE_Peek_id(asn1SccTASTE_Peek_id *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_TASTE_Peek_id_ACN
int Decode_ACN_TASTE_Peek_id(asn1SccTASTE_Peek_id *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_TASTE_Peek_id_NATIVE
int Decode_NATIVE_TASTE_Peek_id(asn1SccTASTE_Peek_id *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySeq_UPER
size_t Encode_UPER_MySeq(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySeq *pSrc);
#endif

#ifdef __NEED_MySeq_ACN
size_t Encode_ACN_MySeq(void *pBuffer, size_t iMaxBufferSize, asn1SccMySeq *pSrc);
#endif

#ifdef __NEED_MySeq_NATIVE
size_t Encode_NATIVE_MySeq(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySeq *pSrc);
#endif

#ifdef __NEED_MySeq_UPER
int Decode_UPER_MySeq(asn1SccMySeq *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySeq_ACN
int Decode_ACN_MySeq(asn1SccMySeq *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySeq_NATIVE
int Decode_NATIVE_MySeq(asn1SccMySeq *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_T_UInt32_UPER
size_t Encode_UPER_T_UInt32(void *pBuffer, size_t iMaxBufferSize, const asn1SccT_UInt32 *pSrc);
#endif

#ifdef __NEED_T_UInt32_ACN
size_t Encode_ACN_T_UInt32(void *pBuffer, size_t iMaxBufferSize, asn1SccT_UInt32 *pSrc);
#endif

#ifdef __NEED_T_UInt32_NATIVE
size_t Encode_NATIVE_T_UInt32(void *pBuffer, size_t iMaxBufferSize, const asn1SccT_UInt32 *pSrc);
#endif

#ifdef __NEED_T_UInt32_UPER
int Decode_UPER_T_UInt32(asn1SccT_UInt32 *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_T_UInt32_ACN
int Decode_ACN_T_UInt32(asn1SccT_UInt32 *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_T_UInt32_NATIVE
int Decode_NATIVE_T_UInt32(asn1SccT_UInt32 *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySimpleSeq_UPER
size_t Encode_UPER_MySimpleSeq(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySimpleSeq *pSrc);
#endif

#ifdef __NEED_MySimpleSeq_ACN
size_t Encode_ACN_MySimpleSeq(void *pBuffer, size_t iMaxBufferSize, asn1SccMySimpleSeq *pSrc);
#endif

#ifdef __NEED_MySimpleSeq_NATIVE
size_t Encode_NATIVE_MySimpleSeq(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySimpleSeq *pSrc);
#endif

#ifdef __NEED_MySimpleSeq_UPER
int Decode_UPER_MySimpleSeq(asn1SccMySimpleSeq *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySimpleSeq_ACN
int Decode_ACN_MySimpleSeq(asn1SccMySimpleSeq *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySimpleSeq_NATIVE
int Decode_NATIVE_MySimpleSeq(asn1SccMySimpleSeq *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_FixedIntList_UPER
size_t Encode_UPER_FixedIntList(void *pBuffer, size_t iMaxBufferSize, const asn1SccFixedIntList *pSrc);
#endif

#ifdef __NEED_FixedIntList_ACN
size_t Encode_ACN_FixedIntList(void *pBuffer, size_t iMaxBufferSize, asn1SccFixedIntList *pSrc);
#endif

#ifdef __NEED_FixedIntList_NATIVE
size_t Encode_NATIVE_FixedIntList(void *pBuffer, size_t iMaxBufferSize, const asn1SccFixedIntList *pSrc);
#endif

#ifdef __NEED_FixedIntList_UPER
int Decode_UPER_FixedIntList(asn1SccFixedIntList *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_FixedIntList_ACN
int Decode_ACN_FixedIntList(asn1SccFixedIntList *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_FixedIntList_NATIVE
int Decode_NATIVE_FixedIntList(asn1SccFixedIntList *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySeqOf_UPER
size_t Encode_UPER_MySeqOf(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySeqOf *pSrc);
#endif

#ifdef __NEED_MySeqOf_ACN
size_t Encode_ACN_MySeqOf(void *pBuffer, size_t iMaxBufferSize, asn1SccMySeqOf *pSrc);
#endif

#ifdef __NEED_MySeqOf_NATIVE
size_t Encode_NATIVE_MySeqOf(void *pBuffer, size_t iMaxBufferSize, const asn1SccMySeqOf *pSrc);
#endif

#ifdef __NEED_MySeqOf_UPER
int Decode_UPER_MySeqOf(asn1SccMySeqOf *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySeqOf_ACN
int Decode_ACN_MySeqOf(asn1SccMySeqOf *pDst, void *pBuffer, size_t iBufferSize);
#endif

#ifdef __NEED_MySeqOf_NATIVE
int Decode_NATIVE_MySeqOf(asn1SccMySeqOf *pDst, void *pBuffer, size_t iBufferSize);
#endif


#endif
